"""Export editable slides and paginated classroom PDFs from the site sources.
Requires reportlab and python-pptx. No cloud service or AI call is used.
"""
import json,re,os,shutil,subprocess,tempfile,sys
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from zipfile import ZipFile,ZIP_DEFLATED
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,KeepTogether,Image
from reportlab.lib.pagesizes import A4
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from teaching import PLANS,slides_for,VERSION

ROOT=Path(__file__).parent
OUT=ROOT/'assets/teaching'
COURSES=json.loads((ROOT/'courses.json').read_text())
BOOKS={b['id']:b for b in json.loads((ROOT/'workbooks.json').read_text())}
FONT=os.environ.get('CLASSROOM_FONT','/System/Library/Fonts/Supplemental/AppleGothic.ttf')
pdfmetrics.registerFont(TTFont('Classroom',FONT))
INK=colors.HexColor('#071126');MUTED=colors.HexColor('#52627a');LIME=colors.HexColor('#c8ff32')
styles={
'body':ParagraphStyle('body',fontName='Classroom',fontSize=10.5,leading=17,spaceAfter=8,textColor=INK,wordWrap='CJK'),
'h1':ParagraphStyle('h1',fontName='Classroom',fontSize=29,leading=38,spaceAfter=20,textColor=INK,wordWrap='CJK'),
'h2':ParagraphStyle('h2',fontName='Classroom',fontSize=19,leading=28,spaceAfter=15,spaceBefore=6,textColor=INK,wordWrap='CJK',keepWithNext=True),
'h3':ParagraphStyle('h3',fontName='Classroom',fontSize=12,leading=19,spaceAfter=8,spaceBefore=10,textColor=INK,wordWrap='CJK',keepWithNext=True),
'small':ParagraphStyle('small',fontName='Classroom',fontSize=8.5,leading=13,spaceAfter=8,textColor=MUTED,wordWrap='CJK'),
'prompt':ParagraphStyle('prompt',fontName='Classroom',fontSize=9.3,leading=14,spaceAfter=13,backColor=colors.HexColor('#f1f4f8'),borderPadding=10,textColor=INK,wordWrap='CJK'),
'cell':ParagraphStyle('cell',fontName='Classroom',fontSize=8.5,leading=13,textColor=INK,wordWrap='CJK')
}
def P(text,style='body'):
    safe=escape(str(text))
    safe=re.sub(r'https?://[^\s<>]+',lambda match:f'<link href="{match[0]}" color="#326390">{match[0]}</link>',safe)
    return Paragraph(safe.replace('\n','<br/>'),styles[style])
def bullets(items):
    return [P('• '+t) for t in items]
def page_decor(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#dde4ed'));canvas.line(42,43,A4[0]-42,43)
    canvas.setFont('Classroom',8);canvas.setFillColor(MUTED)
    canvas.drawString(42,29,'AI BUILDERS LAB · '+VERSION)
    canvas.drawRightString(A4[0]-42,29,str(doc.page))
def pdf(path,story,title):
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=44,bottomMargin=60,title=title,author='AI Builders Lab',pageCompression=1).build(story,onFirstPage=page_decor,onLaterPages=page_decor)
def cover(c,subtitle):
    return [Image(str(ROOT/'assets/builders-lab-logo.png'),width=192,height=64),Spacer(1,50),P('CLASS '+c['number']+' / '+subtitle,'small'),P(c['title'],'h1'),P(PLANS[c['id']]['promise'],'h2'),Spacer(1,18),*bullets(PLANS[c['id']]['objectives']),Spacer(1,30),P('이름 또는 별칭 ____________________\n수업 날짜 ____________________','body'),P('오프라인 현장 실습 · '+VERSION+'\n설명 → 시연 → 함께 실행 → 독립 과제 → 피드백','small'),PageBreak()]
class BlockText(HTMLParser):
    def __init__(self):
        super().__init__();self.blocks=[];self.buf=[];self.kind='body';self.skip=0;self.pre=False
    def flush(self):
        text=''.join(self.buf).strip()
        if text:self.blocks.append((self.kind,text))
        self.buf=[];self.kind='body'
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in ('button','summary','input'): self.skip+=1 if tag!='input' else 0
        if tag in ('h2','h3','p','li','pre','tr'):
            self.flush();self.kind='h2' if tag=='h2' else 'h3' if tag=='h3' else 'prompt' if tag=='pre' else 'body'
            if tag=='li':self.buf.append('• ')
            if tag=='pre':self.pre=True
        if attrs.get('data-os'):self.flush();self.buf.append('Windows 안내\n' if attrs['data-os']=='windows' else 'Mac 안내\n')
        if tag=='br':self.buf.append('\n')
    def handle_data(self,data):
        if not self.skip:self.buf.append(data if self.pre else re.sub(r'\s+',' ',data))
    def handle_endtag(self,tag):
        if tag in ('button','summary') and self.skip:self.skip-=1
        if tag in ('th','td'):self.buf.append(' | ')
        if tag in ('h2','h3','p','li','pre','tr'):
            self.flush()
            if tag=='pre':self.pre=False

def assessment_story(plan):
    a=plan['assignment'];story=[PageBreak(),P('독립 실습 / '+a['title'],'h2'),P(a['task']),P('새 입력 자료','h3'),P(a['input'],'prompt'),P('완료 후 보여줄 것','h3'),*bullets(a['deliverables']),P('도움은 한 단계씩','h3')]
    story+=bullets([f'힌트 {i}: {t}' for i,t in enumerate(plan['rescue'],1)])
    story += [PageBreak(),P('결과를 평가하는 기준','h2'),P('각 항목 0~2점. 권장 통과: 6점 이상이며 모든 항목 1점 이상. 점수만 남기지 말고 관찰한 파일·행동을 기록합니다. 미달 항목은 다른 입력으로 다시 확인합니다.')]
    rows=[[P(x,'cell') for x in ['항목','0 · 다시 해보기','1 · 도움받아 가능','2 · 혼자 가능']]]
    rows += [[P(x,'cell') for x in row] for row in a['rubric']]
    table=Table(rows,colWidths=[76,135,110,186],repeatRows=1,hAlign='LEFT')
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaffbe')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOX',(0,0),(-1,-1),.5,colors.HexColor('#dce3eb')),('INNERGRID',(0,0),(-1,-1),.4,colors.HexColor('#dce3eb')),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
    story+=[table,Spacer(1,18),P('모범 확인 기준 · 먼저 독립 수행한 뒤 읽으세요','h3'),P(a['answer']),P('수업 후 내 일에 적용하기','h3'),P(plan['transfer']),P('마지막 질문','h3'),P(plan['exit']),P('마지막 게임 도전','h3'),P('6개 상황 미션을 모두 해결하고 보스를 클리어하세요. 힌트와 오답 재도전을 사용할 수 있습니다. 실제 실습 결과와 게임 기록을 함께 보여주세요.'),P('https://aihubos.github.io/builderslab-curriculum/mission-'+plan['id']+'.html','small'),PageBreak(),P('내 실행·피드백 기록지','h2')]
    for label in ['오늘의 입력과 출력 파일','내가 직접 작성한 요청','기대한 결과 / 실제 결과','검사한 근거와 미확인 항목','잘된 점 하나 / 다음에 고칠 행동 하나','다시 확인한 결과 / 다음 복습 날짜']:
        story += [P(label,'h3'),P('________________________________________________________________\n\n________________________________________________________________','small'),Spacer(1,9)]
    return story

def export_student(c):
    slug=c['id'];plan=PLANS[slug];story=cover(c,'수강생 워크북')
    story += [P('실습을 시작하기 전에','h2'),P(plan['prep']),P('교재 사용법','h3'),*bullets(['수업에서 시연을 볼 때는 화면을 먼저 관찰합니다. 따라 할 시간에는 한 단계씩 실행합니다.','단계마다 할 일 → 입력 예시 → 정상 결과 → 막혔을 때를 읽습니다.','결과 파일을 실제로 열어본 뒤 완료를 체크합니다. 체크 횟수만으로 학습을 평가하지 않습니다.','다운로드한 ZIP은 압축을 푼 뒤 작업합니다. challenge.txt는 기본 실습을 마친 다음 사용하는 새 과제입니다.','계정 인증과 수강생 기기별 설치는 본인 기기에서 확인합니다. 화면 이름이 다르면 교재의 공식 안내를 함께 봅니다.']),P('시작 상태 기록','h3'),P('설치·계정: 준비 / 도움 필요\n연습 폴더 위치: ____________________\n오늘 혼자 해보고 싶은 것: ____________________')]
    story+=[PageBreak(),P('세 가지 개념부터 이해해요','h2')]
    for x in plan['concepts']:
        story += [P(x['title'],'h3'),P(x['body']),P(x['example'],'prompt'),P('생각해보기: '+x['question'],'small')]
    if slug=='start':
        raw=(ROOT/'lesson-content.html').read_text()
        for section in re.findall(r'<section class="lesson-step" id="step-\d+">.*?</section>',raw,flags=re.S):
            parser=BlockText();parser.feed(section);parser.flush();story.append(PageBreak())
            for kind,text in parser.blocks:
                if text and not text.startswith('＋'):story.append(P(text,kind))
        sources=[['OpenAI 공식 시작 안내','https://learn.chatgpt.com/docs/quickstart'],['Windows 안내','https://learn.chatgpt.com/docs/app/windows'],['데스크톱 앱','https://learn.chatgpt.com/docs/app']]
    else:
        book=BOOKS[slug]
        for i,step in enumerate(book['steps'],1):
            story += [PageBreak(),P(f'{i:02d}. '+step['title'],'h2'),P('할 일','h3'),*bullets(step['do'])]
            for oskey,text in step.get('os',{}).items():
                story += [P('Windows 안내' if oskey=='windows' else 'Mac 안내','h3'),P(text)]
            story += [P('입력 예시','h3'),P(step['prompt'],'prompt'),P('정상 결과','h3'),P(step['expected']),P('막혔을 때','h3'),P(step['trouble']),P('□ '+step['check'],'small')]
        if book.get('extension'):
            x=book['extension'];story += [PageBreak(),P('선택 확장 / '+x['title'],'h2'),*bullets(x['do']),P(x['prompt'],'prompt'),P(x['expected'])]
        sources=book['sources']
    story+=assessment_story(plan)
    story += [PageBreak(),P('개념 질문 확인 답','h2')]
    for x in plan['concepts']:story+=[P(x['question'],'h3'),P(x['answer'])]
    story += [P('공식 참고 · 확인일 2026-09-22','h2'),P('샘플·과제·평가표·설명은 교육용으로 직접 작성했습니다. 제품 지원 환경과 메뉴 이름은 버전에 따라 달라질 수 있습니다.','small')]
    for label,url in sources:story += [P(label,'h3'),P(url,'small')]
    story += [P('온라인 교재','h3'),P('https://aihubos.github.io/builderslab-curriculum/'+('lesson.html' if slug=='start' else f'lesson-{slug}.html'),'small')]
    pdf(OUT/f'{slug}-workbook.pdf',story,c['title']+' · 수강생 워크북')

def text_box(slide,x,y,w,h,text,size,color='071126',bold=False):
    shape=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=shape.text_frame;tf.word_wrap=True;tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0
    for i,line in enumerate(text.split('\n')):
        para=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        para.text=line;para.font.name='맑은 고딕';para.font.size=Pt(size);para.font.bold=bold;para.font.color.rgb=RGBColor.from_string(color);para.space_after=Pt(9);para.line_spacing=1.22
        link=re.search(r'https?://\S+',line)
        if link:
            shape.click_action.hyperlink.address=link[0]
            para.runs[0].font.color.rgb=RGBColor.from_string(color)
            para.runs[0].font.underline=True
    return shape

def export_slides(c):
    deck=Presentation();deck.slide_width=Inches(13.333);deck.slide_height=Inches(7.5)
    deck.core_properties.title=c['title']+' · 현장 강의';deck.core_properties.author='AI Builders Lab'
    slides=slides_for(c)
    for i,s in enumerate(slides,1):
        slide=deck.slides.add_slide(deck.slide_layouts[6]);cover=s.get('kind')=='cover'
        fill=slide.background.fill;fill.solid();fill.fore_color.rgb=RGBColor.from_string('C8FF32' if cover else '071126')
        foreground='071126' if cover else 'FFFFFF';accent='26430D' if cover else 'C8FF32';body='26352E' if cover else 'DBE5F0'
        text_box(slide,.7,.42,11.7,.35,'CLASS '+c['number']+' / '+s['label'],12,accent,True)
        title_size=32 if len(s['title'])>28 else 38
        text_box(slide,.7,1.0,11.9,1.8,s['title'],title_size,foreground,True)
        longest=max(map(len,s['lines']));size=23 if longest<90 else 21 if longest<165 else 19
        text_box(slide,.8,2.85,11.7,3.5,'\n'.join('• '+t for t in s['lines']),size,body)
        text_box(slide,.7,6.96,10.5,.25,'AI BUILDERS LAB / '+VERSION,9,accent)
        text_box(slide,11.55,6.89,1.1,.32,f'{i:02d} / {len(slides)}',12,accent,True)
        slide.notes_slide.notes_text_frame.text=s['notes']
    deck.save(OUT/f'{c["id"]}-slides.pptx')

def instructor():
    story=[Image(str(ROOT/'assets/builders-lab-logo.png'),width=192,height=64),Spacer(1,50),P('현장 강의 운영안','h1'),P('시연에서 독립 수행까지','h2'),P('오프라인 현장 실습 · '+VERSION),P('권장 시간은 설치 준비 완료를 기준으로 한 설계입니다. 실제 일정·가격·정원을 확정한 모집 안내가 아닙니다.'),PageBreak(),P('강의 전 준비','h2')]
    story+=bullets(['개설 시 확정: 강사 소개·일정·장소·정원·수강료·신청 및 취소 안내·질문 채널·보충 시간. 임의로 이력을 만들지 않습니다.','수업 전: 준비 안내를 전달하고 설치·계정 도움이 필요한 수강생을 파악합니다. 계정 비밀번호와 인증코드는 수집하지 않습니다.','강사 리허설: 새 연습 폴더에서 교재의 요청을 실행하고 실제 결과·두 번째 입력·오류 상황을 확인합니다. 인증은 본인 계정으로 직접 수행합니다.','당일: 화면 공유 시 다른 문서를 닫고 글자를 크게 표시합니다. 와이파이·전원·다운로드·실습 파일을 확인합니다.','단계 전환: 완료 / 도움 필요를 확인합니다. 수강생이 조작할 수 있게 진행자가 대신 클릭하는 시간을 최소화합니다.'])
    story += [P('진도 차이와 장애 대응','h2'),*bullets(['첫 시연은 보기만 합니다. 그다음 한 단계씩 같이 실행합니다. 설치·계정이 안 된 학습자를 기다리며 전체가 멈추기보다 관찰과 개별 도움을 구분합니다.','빠른 학습자는 기능 확장 대신 원문 대조·새 입력 비교를 합니다. 다른 학습자의 컴퓨터를 대신 완료시키지 않습니다.','힌트 순서: 질문으로 위치를 찾게 함 → 행동 하나만 보여줌 → 수강생이 다른 입력으로 다시 실행.','인터넷·인증 장애: 내려받은 샘플과 모범 기준으로 오류 찾기·요청 설계를 합니다. AI 실행과 설치는 미완료로 남겨 보충합니다.','평가: 결과 파일 또는 실제 동작을 확인합니다. 4항목 각 0~2점. 6점 이상이며 0점 항목이 없을 때 기본 수행으로 봅니다. 관찰 근거 없이 점수만 적지 않습니다.','피드백: 잘된 행동 한 가지 → 근거 → 다음에 할 행동 한 가지. 미달 항목은 다음 입력으로 재확인합니다.']),P('수업 종료 기록','h2'),P('과정 / 학습자 별칭 / 막힌 단계 / 도움 수준 / 결과 위치 / 평가 근거 / 다음 재시도 / 보충 약속을 기록합니다. 기록과 파일 공유는 수강생 동의를 받고 필요한 범위로 합니다.')]
    for c in COURSES:
        p=PLANS[c['id']]
        story += [PageBreak(),P('CLASS '+c['number']+' / '+c['title'],'h2'),P(f"권장 {p['minutes']}분 · 휴식 10분 포함"),P(p['prep']),*bullets(p['objectives'])]
        elapsed=0
        for row in p['agenda']:
            end=elapsed+row['minutes']
            story += [P(f'{elapsed}–{end}분 / '+row['title'],'h3'),P('교재 '+row['steps']+' · '+row['activity']),P('강사 발문: “'+row['script']+'”'),P('관찰 기준: '+row['checkpoint'],'small')]
            elapsed=end
        story += [P('오개념 교정','h3'),P(p['pitfall']['bad']),P(p['pitfall']['why']+' '+p['pitfall']['fix']),P('도움 순서','h3'),*bullets(p['rescue']),P('독립 과제 확인 답','h3'),P(p['assignment']['answer']),P('마지막 질문','h3'),P(p['exit']),P('마무리 게임: https://aihubos.github.io/builderslab-curriculum/mission-'+c['id']+'.html','small'),P('게임에서 6개 상황 판단을 모두 해결하게 합니다. 오답은 해설과 재도전으로 이해를 확인하세요. 실제 실습 결과와 게임 클리어를 함께 확인하며, 게임 통과가 기기 설치나 결과 파일의 실제 검증을 대신하지 않습니다.','small')]
    pdf(OUT/'instructor-guide.pdf',story,'AI 빌더스랩 · 현장 강의 운영안')


def handout_prompt(slug):
    if slug=='start':return (ROOT/'assets/request-template.txt').read_text().strip()
    index={'workflow':2,'wiki':2,'hermes':5,'web':2,'app':2}[slug]
    return BOOKS[slug]['steps'][index]['prompt']

def handout_story(c):
    p=PLANS[c['id']];slug=c['id'];a=p['assignment']
    url='https://aihubos.github.io/builderslab-curriculum/'+('lesson.html' if slug=='start' else 'lesson-'+slug+'.html')
    story=[Image(str(ROOT/'assets/builders-lab-logo.png'),width=156,height=52),Spacer(1,18),P('CLASS '+c['number']+' / 수강생 공유용 · 1. 준비와 이해','small'),P(c['title'],'h1'),P(p['promise']),P('오늘 할 수 있게 될 일','h3'),*bullets(p['objectives']),P('시작 전에','h3'),P(p['prep'])]
    for x in p['concepts']:story += [P(x['title'],'h3'),P(x['example'],'small')]
    story += [P('설치·폴더 선택부터 자세히 따라 하려면','h3'),P(url,'small'),PageBreak(),P('2. 내 컴퓨터에서 실행하기','h2'),*bullets(['과정 ZIP을 다운로드하고 압축을 풉니다. START-HERE.txt가 있는 폴더를 엽니다.','교재에서 앞 단계를 마친 후 아래 대표 요청을 보냅니다. Hermes 과정은 Hermes에, 나머지 과정은 Codex에 입력합니다.','작업이 끝나면 실제 결과 파일이나 앱을 열어 확인합니다. 아래 요청은 앞 단계의 설치·폴더 준비를 건너뛰는 명령이 아닙니다.']),P('대표 실습 요청 · 파일 이름을 확인한 뒤 사용','h3'),P(handout_prompt(slug),'prompt'),P('직접 확인할 것','h3'),*bullets(c['completion']),P('막히면 네 줄로 설명해요','h3'),P('막힌 단계: ____ / 내가 한 행동: ____\n기대한 결과: ____ / 실제 결과·오류 문구: ____','prompt'),PageBreak(),P('3. 새 자료로 혼자 해보기','h2'),P(a['title'],'h3'),P(a['task']),P(a['input'],'prompt'),P('완료 후 보여줄 것','h3'),*bullets(a['deliverables']),P('내일 한 번 더','h3'),P(p['transfer']),P('나의 기록','h3'),P('결과 파일 위치: _________________________________\n잘된 점: _______________________________________\n다음에 고칠 행동: _______________________________\n다시 해볼 날짜: _________________________________'),P('실습 후 게임: https://aihubos.github.io/builderslab-curriculum/mission-'+slug+'.html\n상세 실습: '+url,'small')]
    return story

def export_handouts():
    all_story=[]
    for c in COURSES:
        slug=c['id'];p=PLANS[slug];a=p['assignment']
        pdf(OUT/f'{slug}-handout.pdf',handout_story(c),c['title']+' · 수강생 요약')
        if all_story:all_story.append(PageBreak())
        all_story.extend(handout_story(c))
        md=['# '+c['title']+' · 수강생 공유용',p['promise'],'## 오늘의 목표',*['- '+x for x in p['objectives']],'## 준비',p['prep']]
        for x in p['concepts']:md+=['### '+x['title'],x['example']]
        md+=['## 대표 실습 요청','앞 단계의 설치·폴더 준비를 마친 후 사용합니다.','```text',handout_prompt(slug),'```','## 결과 확인',*['- '+x for x in c['completion']],'## 혼자 해보기',a['title'],a['task'],'```text',a['input'],'```','## 보여줄 결과',*['- '+x for x in a['deliverables']],'## 복습',p['transfer'],'## 실습 후 게임','https://aihubos.github.io/builderslab-curriculum/mission-'+slug+'.html','6개 상황 미션을 모두 해결하고 보스를 클리어하세요. 힌트·오답 재도전이 가능합니다. 실습 결과도 직접 확인하세요.','## 기록','결과 파일 위치:\n잘된 점:\n다음에 고칠 행동:\n다시 해볼 날짜:']
        (OUT/f'{slug}-handout.md').write_text('\n\n'.join(md)+'\n')
    pdf(OUT/'student-handouts.pdf',all_story,'AI 빌더스랩 · 수강생 공유용 요약 교재')


def render_slide_pdfs():
    binary=shutil.which('soffice')
    if not binary:raise RuntimeError('슬라이드 PDF 생성에는 LibreOffice soffice가 필요합니다. 설치 후 다시 실행하세요.')
    with tempfile.TemporaryDirectory(prefix='builderslab-docs-') as temp:
        folder=Path(temp);env=os.environ.copy()
        if sys.platform=='darwin':
            config=folder/'fonts.conf'
            config.write_text('<?xml version="1.0"?><fontconfig><dir>/System/Library/Fonts</dir><dir>/System/Library/Fonts/Supplemental</dir><cachedir>'+str(folder/'font-cache')+'</cachedir><alias><family>맑은 고딕</family><prefer><family>AppleGothic</family></prefer></alias></fontconfig>')
            env['FONTCONFIG_FILE']=str(config)
        subprocess.run([binary,'--headless','-env:UserInstallation='+(folder/'profile').as_uri(),'--convert-to','pdf','--outdir',str(OUT)]+[str(OUT/f'{c["id"]}-slides.pptx') for c in COURSES],check=True,env=env,stdout=subprocess.DEVNULL,timeout=120)
if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    for c in COURSES:
        export_student(c);export_slides(c)
        print(c['id'],'PDF + PPTX',len(slides_for(c)),'slides')
    instructor()
    export_handouts()
    render_slide_pdfs()
    print('PDF, PPTX and rendered slide PDFs complete. Run build.py to refresh archives.')
