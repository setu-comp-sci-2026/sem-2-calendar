from pathlib import Path
from datetime import date,timedelta
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.colors import HexColor
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'calendar.yaml').read_text()
weeks=[]
for d,n,t in re.findall(r'  - date: (\d{4}-\d{2}-\d{2})\s+week: (\d+|~)\s+topic: ([^\n]+)',raw):
    weeks.append((date.fromisoformat(d),int(n) if n!='~' else None,t))
assert len(weeks)==17
out=ROOT/'unit-1-sem-2/paneltalk-1-calendar/calendar.pdf'
c=canvas.Canvas(str(out),pagesize=landscape(A4))
c.setTitle('Semester 2 Calendar 2027');c.setAuthor('Department of Computing & Mathematics, SETU')
W,H=landscape(A4)
left=30;top=H-75
widths=[55,68]+[43]*7+[153]
xs=[left]
for width in widths:xs.append(xs[-1]+width)
rowh=22
c.setFillColor(HexColor('#626262'));c.setFont('Helvetica-Bold',19)
c.drawString(left,H-34,'Semester 2 | 2027')
c.setFont('Helvetica',10);c.drawRightString(W-30,H-33,'Monday - Sunday')
c.setFillColor(HexColor('#F2F2F2'));c.rect(left,top,xs[-1]-left,25,fill=1,stroke=0)
c.setFillColor(HexColor('#626262'));c.setFont('Helvetica-Bold',10)
c.drawString(left+5,top+9,'Semester 2')
for j,lab in enumerate(['Mon','Tue','Wed','Thu','Fri','Sat','Sun']):c.drawCentredString((xs[j+2]+xs[j+3])/2,top+9,lab)
c.drawCentredString((xs[9]+xs[10])/2,top+9,'Modules / events')
c.setStrokeColor(HexColor('#555555'));c.setLineWidth(.5);c.line(left,top,xs[-1],top)
prev=''
for i,(mon,num,topic) in enumerate(weeks):
    y=top-(i+1)*rowh
    month=(mon+timedelta(days=6)).strftime('%B')
    if topic in ['Reading Week','Easter Break']:
        c.setFillColor(HexColor('#FFF3D6' if topic=='Reading Week' else '#EEE8F5'))
        c.rect(xs[2],y,xs[-1]-xs[2],rowh,fill=1,stroke=0)
    if num is not None:
        for col,color in [(2,'#FF0000'),(4,'#FF0000'),(5,'#0070C0')]:
            c.setFillColor(HexColor(color))
            c.rect(xs[col],y,widths[col],rowh,fill=1,stroke=0)
    if i==0:
        c.setFillColor(HexColor('#DCEEE5'));c.rect(xs[6],y,widths[6],rowh,fill=1,stroke=0);c.rect(xs[9],y,widths[9],rowh,fill=1,stroke=0)
    c.setFillColor(HexColor('#626262'));c.setFont('Helvetica-Bold',10)
    if month!=prev:c.drawString(xs[0]+5,y+7,month);prev=month
    label=str(num) if num else 'reading-week' if topic=='Reading Week' else 'EASTER' if topic=='Easter Break' else ''
    c.setFont('Helvetica-BoldOblique',9);c.drawRightString(xs[2]-6,y+7,label)
    c.setFillColor(HexColor('#222222'));c.setFont('Helvetica',11)
    for day in range(7):
        if i==0 and day==4:c.setFillColor(HexColor('#20533D'));c.setFont('Helvetica-Bold',11)
        c.drawRightString(xs[day+3]-6,y+7,str((mon+timedelta(days=day)).day))
        c.setFillColor(HexColor('#222222'));c.setFont('Helvetica',11)
    if i==0:
        c.setFillColor(HexColor('#20533D'));c.setFont('Helvetica-Bold',9)
        c.drawString(xs[9]+6,y+7,'15 Jan: January On-Site')
    elif num is not None:
        c.setFillColor(HexColor('#222222'));c.setFont('Helvetica',9)
        c.drawCentredString((xs[9]+xs[10])/2,y+7,'comp sys & database')
    c.setStrokeColor(HexColor('#555555'))
    for x in xs[2:]:c.line(x,y,x,y+rowh)
    c.line(xs[2],y,xs[-1],y)
c.line(xs[2],top,xs[-1],top)
bottom=top-len(weeks)*rowh
c.setFillColor(HexColor('#626262'));c.setFont('Helvetica',9)
c.drawString(left,bottom-23,'Red: Computer Systems & Networks (Mon / Wed). Blue: Database (Thu).')
c.drawString(left,bottom-39,'Teaching: 18 January - 7 May 2027. January On-Site: Friday 15 January 2027.')
c.drawString(left,bottom-55,'Reading weeks and Easter are shaded separately. Webinar times and assessments will follow.')
key_x=xs[-1]+28
c.setFont('Helvetica-Bold',11);c.drawString(key_x,top+9,'Delivery key')
for image,label,y in [('computer-systems.png','Red: Mon / Wed',top-185),('database.png','Blue: Thursday',top-374)]:
    c.setFont('Helvetica',9);c.setFillColor(HexColor('#626262'))
    c.drawString(key_x,y+170,label)
    c.drawImage(str(ROOT/'scripts/assets'/image),key_x,y,width=105,height=166,mask='auto')
c.setFont('Helvetica',8);c.drawString(left,24,'SETU | Department of Computing & Mathematics');c.drawRightString(W-30,24,'1')
c.save()
r=PdfReader(out)
assert len(r.pages)==1
text=r.pages[0].extract_text()
assert '15 Jan: January On-Site' in text
assert text.count('reading-week')==2 and text.count('EASTER')==2
assert text.count('comp sys & database')==12
assert len(r.pages[0].images)==2
print(out)
