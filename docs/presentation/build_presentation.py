"""Build an editable, dependency-free presentation and matching contact sheet."""
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
SLIDES = [
 ('EMG Motion Rhythm', '손의 움직임과 근육의 수축을 리듬으로 연결하다', [('HAND', '손가락 개수로 레인 선택'), ('EMG', '근전도 수축으로 타이밍 입력')], 15,
  '안녕하세요. EMG Motion Rhythm은 손 추적과 근전도를 결합한 리듬게임입니다. 손가락 개수로 위치를 선택하고, 근육을 수축해 음악의 타이밍에 맞춰 노트를 처리합니다.'),
 ('어디를 칠지, 언제 칠지', '두 입력이 서로 다른 역할을 담당합니다', [('01  손가락 → 레인', '펼친 손가락 1~5개 = 1~5번 레인\n주먹은 레인을 선택하지 않음'), ('02  수축 → 판정', '노트가 판정선에 도착할 때 수축\n레인과 타이밍이 맞으면 HIT')], 30,
  '조작은 두 단계입니다. 먼저 웹캠 앞에서 펼친 손가락 개수로 다섯 개 레인 중 하나를 선택합니다. 예를 들어 세 개를 펴면 세 번째 레인입니다. 그다음 노트가 판정선에 도착할 때 근육을 수축합니다. 즉, 손은 어디를 칠지 결정하고 근전도는 언제 칠지 결정합니다. 주먹 상태에서는 레인이 선택되지 않습니다.'),
 ('두 신호를 하나의 게임 입력으로', 'MediaPipe 손 추적 + 시리얼 EMG → InputFusion → 게임 판정', [('손 추적', '웹캠 영상\nMediaPipe가 손가락 개수 인식'), ('근전도', '센서의 시리얼 신호\n설정한 ON/OFF 기준으로 활성 판단'), ('입력 결합', '선택 레인 + EMG 활성 상태\n동일한 게임 입력 상태로 전달')], 40,
  '시스템은 손 추적과 근전도 입력을 각각 처리한 뒤 결합합니다. 웹캠 영상에서는 MediaPipe가 손을 추적하고 펼친 손가락 수를 계산합니다. 근전도 센서는 시리얼 통신으로 값을 전달하며, 설정된 활성과 이완 기준으로 입력 상태를 판단합니다. InputFusion은 레인과 근전도 상태를 묶어 게임에 전달합니다. 설정 화면에서는 안정 상태와 반복 수축을 측정해 보정값을 저장할 수 있습니다. 사용자의 실제 입력을 하나의 게임 조작으로 연결하는 구조입니다.'),
 ('한 번의 수축, 최대 한 개의 노트', '레인 일치와 타이밍을 함께 확인합니다', [('입력 조건', '선택한 레인 = 노트 레인\n이완 후 새 수축이 발생'), ('판정 결과', 'PERFECT · GOOD · MISS\n점수와 콤보로 즉시 피드백')], 40,
  '게임에서는 레인이 맞는지, 판정 시간 안에 수축했는지를 확인합니다. 특히 근육에 계속 힘을 주고 있다고 노트를 연속으로 처리하지 않습니다. 이완한 뒤 다시 수축했을 때 새로운 입력으로 인식하며, 한 번의 수축으로는 최대 한 노트만 판정합니다. 타이밍에 따라 PERFECT 또는 GOOD을 받고, 판정 시간을 지나면 MISS가 됩니다. 결과는 화면의 점수와 콤보로 바로 확인할 수 있습니다. 손의 자세 선택과 근육의 반복 수축이 모두 필요한 방식입니다.'),
 ('음악 선택부터 결과 확인까지', '반복해서 플레이할 수 있는 로컬 실행 흐름', [('음악과 노트', 'MP3 · WAV · OGG 추가\n음악 분석으로 노트 생성·저장\n저장된 음악과 노트 다시 불러오기'), ('결과와 기록', '게임 결과 화면 확인\n입력·판정 세션을 JSON / CSV 저장\nWindows 실행 파일 제공')], 45,
  '플레이 흐름은 음악 추가, 노트 생성, 게임 진행, 결과 확인 순서입니다. MP3, WAV, OGG 파일을 추가할 수 있고 음악 분석 결과로 노트를 생성해 저장합니다. 저장된 노트는 다음 실행에서 다시 불러올 수 있습니다. 게임이 끝나면 결과를 확인하고, 입력과 판정 정보는 로컬 JSON과 CSV 파일로 남깁니다. 실제 센서가 없는 개발 환경에서는 모의 근전도 입력으로 판정을 점검할 수도 있습니다. 현재 구현은 Windows 데스크톱 앱이며, 이번 발표에서는 실제로 구현된 입력 결합과 플레이 흐름에 집중하겠습니다.'),
 ('이제 실제 플레이로 확인하겠습니다', '손으로 선택하고, 근육으로 타이밍을 맞춥니다', [('시연 관찰 포인트', '① 손가락 개수에 따른 레인 변화\n② 수축 시점의 판정·콤보\n③ 게임 종료 후 결과 확인')], 10,
  '이어서 두 분 정도의 시연 영상입니다. 손가락에 따른 레인 변화, 수축 타이밍의 판정, 마지막 결과 화면을 중심으로 봐주시면 됩니다.'),
 ('시연 영상', 'DEMO  /  약 2분', [('▶', '이 영역에 시연영상을 삽입하세요\n권장 화면 비율 16:9')], 120,
  '영상 삽입 전 가운데 안내 상자를 삭제하고 삽입 → 비디오 → 이 장치에서 파일을 선택합니다. 시작은 자동 또는 클릭 시로 설정합니다. 권장 구성: 0:00~0:20 음악 선택과 준비, 0:20~1:40 손가락 레인 선택과 EMG 플레이, 1:40~2:00 결과 확인. 아직 영상 파일이 제공되지 않아 영상은 포함되지 않았습니다.'),
]
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
def xml(s): return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+s
def box(i,x,y,w,h,text,size=24,color='172A3A',fill=None,bold=False):
    paras=''.join(f'<a:p><a:r><a:rPr lang="ko-KR" sz="{size*100}" b="{int(bold)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="맑은 고딕"/><a:ea typeface="맑은 고딕"/></a:rPr><a:t>{escape(t)}</a:t></a:r><a:endParaRPr lang="ko-KR"/></a:p>' for t in text.split('\n'))
    return f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="Text {i}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{int(x*914400)}" y="{int(y*914400)}"/><a:ext cx="{int(w*914400)}" cy="{int(h*914400)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{f"<a:solidFill><a:srgbClr val='{fill}'/></a:solidFill>" if fill else "<a:noFill/>"}<a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="100000" tIns="70000" rIns="100000" bIns="70000"/><a:lstStyle/>{paras}</p:txBody></p:sp>'
def group(): return '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
def rels(items): return xml(f'<Relationships xmlns="{REL}">'+''.join(f'<Relationship Id="{i}" Type="{R}/{t}" Target="{v}"/>' for i,t,v in items)+'</Relationships>')
def build():
    overrides=[('/ppt/presentation.xml','presentationml.presentation.main'),('/ppt/slideMasters/slideMaster1.xml','presentationml.slideMaster'),('/ppt/slideLayouts/slideLayout1.xml','presentationml.slideLayout')]
    with ZipFile(OUT/'EMG-Motion-Rhythm-5min.pptx','w',ZIP_DEFLATED) as z:
        for j,(title,sub,cards,secs,note) in enumerate(SLIDES,1):
            shapes=group()+box(2,0,0,13.333,.12,'',fill='176B63')+box(3,.55,.4,12,.35,'EMG MOTION RHYTHM   /   PROJECT PRESENTATION',12,'176B63',bold=True)+box(4,.55,1,12,1.15,title,34,bold=True)+box(5,.55,2.05,12,.65,sub,19,'526570')
            n=len(cards); width=12.1/n
            for k,(head,body) in enumerate(cards):
                x=.6+k*width
                shapes+=box(10+k*3,x,3,width-.18,2.75,'',fill='EDF3F2')+box(11+k*3,x+.15,3.2,width-.48,.7,head,25,'176B63',bold=True)+box(12+k*3,x+.15,4,width-.48,1.6,body,20)
            shapes+=box(40,.6,6.55,11,.4,'EXTRACTED · README 및 현재 소스에서 확인한 구현' if j<7 else '영상 삽입: 삽입 → 비디오 → 이 장치',11,'526570')+box(41,12,6.55,.8,.4,f'{j:02}',12,'176B63')
            z.writestr(f'ppt/slides/slide{j}.xml',xml(f'<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree>{shapes}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr><p:timing/></p:sld>'))
            z.writestr(f'ppt/slides/_rels/slide{j}.xml.rels',rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','notesSlide',f'../notesSlides/notesSlide{j}.xml')]))
            z.writestr(f'ppt/notesSlides/notesSlide{j}.xml',xml(f'<p:notes xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:spTree>{group()}{box(2,1,1,6,8,f"발표 시간: {secs}초 / "+note,14)}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'))
            z.writestr(f'ppt/notesSlides/_rels/notesSlide{j}.xml.rels',rels([('rId1','slide',f'../slides/slide{j}.xml')]))
            overrides.extend([(f'/ppt/slides/slide{j}.xml','presentationml.slide'),(f'/ppt/notesSlides/notesSlide{j}.xml','presentationml.notesSlide')])
        z.writestr('[Content_Types].xml',xml('<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'+''.join(f'<Override PartName="{p}" ContentType="application/vnd.openxmlformats-officedocument.{t}+xml"/>' for p,t in overrides)+'</Types>'))
        z.writestr('_rels/.rels',rels([('rId1','officeDocument','ppt/presentation.xml')]))
        z.writestr('ppt/presentation.xml',xml(f'<p:presentation xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdMaster"/></p:sldMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1,8))+'</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>'))
        z.writestr('ppt/_rels/presentation.xml.rels',rels([('rIdMaster','slideMaster','slideMasters/slideMaster1.xml')]+[(f'rId{i}','slide',f'slides/slide{i}.xml') for i in range(1,8)]))
        cmap='<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
        z.writestr('ppt/slideMasters/slideMaster1.xml',xml(f'<p:sldMaster xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:cSld><p:spTree>{group()}</p:spTree></p:cSld>{cmap}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'))
        z.writestr('ppt/slideMasters/_rels/slideMaster1.xml.rels',rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml')]))
        z.writestr('ppt/slideLayouts/slideLayout1.xml',xml(f'<p:sldLayout xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}" type="blank"><p:cSld name="Blank"><p:spTree>{group()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'))
        z.writestr('ppt/slideLayouts/_rels/slideLayout1.xml.rels',rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml')]))
    script='# 5분 발표 대본\n\n본문 180초 + 시연 120초. 실제 발화 속도에 따라 리허설로 조정하세요.\n\n'
    for i,(t,s,c,sec,n) in enumerate(SLIDES,1): script+=f'## {i}. {t} — {sec}초\n\n{n}\n\n'
    (OUT/'speaker-script.md').write_text(script,encoding='utf-8')
    preview=Image.new('RGB',(1280,360*4),'#dce4e4')
    for j,(title,sub,cards,secs,note) in enumerate(SLIDES):
        im=Image.new('RGB',(1280,720),'white'); d=ImageDraw.Draw(im)
        def text(x,y,t,size,color='#172A3A',bold=False):
            font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf' if bold else 'C:/Windows/Fonts/malgun.ttf',size)
            d.multiline_text((x,y),t,font=font,fill=color,spacing=14)
        d.rectangle((0,0,1280,12),fill='#176B63'); text(60,45,'EMG MOTION RHYTHM  /  PROJECT PRESENTATION',18,'#176B63',True)
        text(60,110,title,46,bold=True);text(60,210,sub,25,'#526570')
        for k,(h,b) in enumerate(cards):
            w=1160/len(cards);x=int(60+k*w);d.rectangle((x,300,x+w-18,580),fill='#edf3f2');text(x+20,325,h,30,'#176B63',True);text(x+20,410,b,24)
        text(60,657,'EXTRACTED · README 및 현재 소스에서 확인한 구현' if j<6 else '영상 삽입: 삽입 → 비디오 → 이 장치',16,'#526570');text(1180,657,f'{j+1:02}',18)
        preview.paste(im.resize((640,360)),((j%2)*640,(j//2)*360))
    preview.save(OUT/'content-layout-preview.png')
    print('Created PPTX, speaker script, and layout preview. Body:',sum(s[3] for s in SLIDES[:-1]),'seconds.')
def apply_template():
    import xml.etree.ElementTree as E
    E.register_namespace('p',P); E.register_namespace('a',A); E.register_namespace('r',R)
    ns={'p':P,'a':A,'r':R}
    def fragment(s):
        return E.fromstring(f'<root xmlns:p="{P}" xmlns:a="{A}">'+s+'</root>')[0]
    selected=[1,3,9,11,18,4,8]
    values=[
      ['EMG Motion\nRhythm','본문 3분 + 시연 2분','FORMAT','프로젝트 발표','EMG + HAND TRACKING','TIME','손 추적 × 근전도','INPUT','EMG Motion Rhythm'],
      ['어디를 칠지, 언제 칠지','손가락은 레인을, 근전도는 타이밍을 결정합니다.','EMG Motion Rhythm','02','펼친 손가락 1~5개가 각각 1~5번 레인을 선택합니다. 주먹은 레인을 선택하지 않습니다.','노트가 판정선에 도착할 때 근육을 수축합니다. 선택 레인과 타이밍이 맞으면 HIT입니다.','손의 자세와 근육의 수축을 결합한 5레인 리듬게임입니다.','손가락 → 레인 선택','수축 → 타이밍 입력','두 입력을 결합','조작','핵심 원리'],
      ['EMG Motion Rhythm','03','두 신호를 하나의 입력으로','손 추적과 근전도를 결합해 게임 판정에 전달합니다.','입력\n결합','손 추적','웹캠 영상에서 MediaPipe로 손을 추적하고 펼친 손가락 개수를 계산합니다.','근전도','센서의 시리얼 신호를 읽고 ON/OFF 기준으로 활성 상태를 판단합니다.','보정','InputFusion','안정 상태와 반복 수축을 측정해 개인의 입력 기준을 설정·저장합니다.','레인과 근전도 상태를 묶어 게임의 입력 상태로 전달합니다.'],
      ['EMG Motion Rhythm','04','한 번의 수축, 한 개의 노트','레인 일치와 타이밍을 함께 확인합니다.','손으로 선택한 레인과 현재 노트의 레인이 일치해야 합니다.','01  레인 일치','판정 시간 안에 새로운 수축이 발생하면 입력으로 인식합니다.','02  타이밍 확인','계속 힘을 주어도 연속 입력되지 않습니다. 이완 후 다시 수축해야 합니다.','03  수축당 최대 한 노트','PERFECT · GOOD · MISS로 판정하고 점수와 콤보를 표시합니다.','04  즉시 피드백'],
      ['EMG Motion Rhythm','05','종료 후 결과를 확인하고 입력·판정 기록을 로컬 JSON / CSV로 저장합니다.','음악에 맞춰 레인을 선택하고 수축으로 노트를 처리합니다.','음악 분석으로 노트를 생성·저장합니다. 저장된 노트는 다시 불러옵니다.','MP3 · WAV · OGG 파일을 추가하고 저장된 음악을 선택합니다.','음악에서 결과까지','음악 추가 → 노트 생성 → 플레이 → 결과 확인','04  결과와 기록','03  게임 진행','02  노트 생성','01  음악 선택'],
      ['시연으로 확인할 핵심','손으로 선택하고, 근육으로 타이밍을 맞춥니다.','EMG Motion Rhythm','06','손가락 개수에 따른 레인 변화와 수축 시점의 판정·콤보를 확인해주세요. 마지막에는 게임 결과 화면을 보여드립니다.','Windows 데스크톱 앱으로 구현했습니다. 이번 발표는 실제 구현된 입력 결합과 플레이 흐름을 소개합니다.','시연 관찰 포인트','현재 구현 범위'],
      ['EMG Motion Rhythm','07','시연 영상','약 2분 · 손가락 레인 선택 → EMG 플레이 → 결과 확인','','','',''],
    ]
    path=OUT/'EMG-Motion-Rhythm-5min.pptx'
    with ZipFile(path) as generated: notes={n:generated.read(n) for n in generated.namelist() if n.startswith('ppt/notesSlides/')}
    with ZipFile(OUT/'design-template.pptx') as src:
      data={n:src.read(n) for n in src.namelist()}
    for j,old in enumerate(selected,1):
      name=f'ppt/slides/slide{old}.xml'; root=E.fromstring(data[name]); shapes=[s for s in root.findall('.//p:sp',ns) if s.findall('.//a:t',ns)]
      assert len(shapes)==len(values[j-1]),(old,len(shapes))
      for sp,new in zip(shapes,values[j-1]):
        tb=sp.find('p:txBody',ns); ps=tb.findall('a:p',ns); first=ps[0]; runs=first.findall('a:r',ns)
        for p in ps[1:]:tb.remove(p)
        for child in list(first):
          if child.tag not in [f'{{{A}}}pPr']:first.remove(child)
        import copy
        base=copy.deepcopy(runs[0].find('a:rPr',ns)) if runs else E.Element(f'{{{A}}}rPr')
        for k,line in enumerate(new.split('\n')):
          if k:E.SubElement(first,f'{{{A}}}br')
          run=E.SubElement(first,f'{{{A}}}r');run.append(copy.deepcopy(base));E.SubElement(run,f'{{{A}}}t').text=line
      tree=root.find('p:cSld/p:spTree',ns)
      if j==7:
        for parent in root.iter():
          for ch in list(parent):
            if ch.tag==f'{{{P}}}pic':parent.remove(ch)
        # Video slot uses editable shapes, with the template header retained.
        for sp in list(tree):
          if sp.tag==f'{{{P}}}sp' and sp not in shapes[:4]:tree.remove(sp)
        tree.append(fragment(box(900,1.3,3.3,17.4,6.5,'',fill='EDF3F2')))
        tree.append(fragment(box(901,2,5,16,1,'▶  시연영상을 삽입하세요',36,'154C45',bold=True)))
        tree.append(fragment(box(902,2,6.3,16,.6,'16:9  /  약 2분  /  삽입 → 비디오 → 이 장치',20,'595959')))
      tree.append(fragment(box(950,.5,10.75,18,.3,'EXTRACTED · README / 현재 소스 확인' if j<7 else '시연영상 파일은 추후 삽입',10,'595959')))
      timing=root.find('p:timing',ns)
      if timing is not None:root.remove(timing)
      data[name]=E.tostring(root,encoding='utf-8',xml_declaration=True)
      rn=f'ppt/slides/_rels/slide{old}.xml.rels'; rr=E.fromstring(data[rn])
      for ch in list(rr):
        if ch.attrib.get('Type','').endswith('/notesSlide'):rr.remove(ch)
      E.SubElement(rr,f'{{{REL}}}Relationship',Id='rIdPresentationNotes',Type=R+'/notesSlide',Target=f'../notesSlides/notesSlide{j}.xml')
      data[rn]=E.tostring(rr,encoding='utf-8',xml_declaration=True)
      notes[f'ppt/notesSlides/_rels/notesSlide{j}.xml.rels']=rels([('rId1','slide',f'../slides/slide{old}.xml')]).encode()
    root=E.fromstring(data['ppt/presentation.xml']); ids=root.find('p:sldIdLst',ns); original=list(ids)
    for ch in original:ids.remove(ch)
    for old in selected:ids.append(original[old-1])
    data['ppt/presentation.xml']=E.tostring(root,encoding='utf-8',xml_declaration=True)
    data.update(notes)
    ct=E.fromstring(data['[Content_Types].xml']); known={x.attrib.get('PartName') for x in ct}
    for i in range(1,8):
      part=f'/ppt/notesSlides/notesSlide{i}.xml'
      if part not in known:E.SubElement(ct,'{http://schemas.openxmlformats.org/package/2006/content-types}Override',PartName=part,ContentType='application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml')
    data['[Content_Types].xml']=E.tostring(ct,encoding='utf-8',xml_declaration=True)
    with ZipFile(path,'w',ZIP_DEFLATED) as out:
      for n,b in data.items():out.writestr(n,b)
    print('Applied original template slides:',selected)
if __name__=='__main__':
    build()
    if (OUT/'design-template.pptx').exists(): apply_template()
