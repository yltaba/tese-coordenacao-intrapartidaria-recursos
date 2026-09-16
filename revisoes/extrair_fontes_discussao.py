from pathlib import Path
import fitz
import json

base=Path('G:/Meu Drive/recursos-campanha/literatura/textos_prioritarios')
out=Path(__file__).parent/'fontes-discussao-capitulo3'
out.mkdir(exist_ok=True)
prefixes={'cheibub':'Cheibub Sin 2020','thomsen':'Thomsen 2023','silvacodato':'Silva e Codato 2024',
          'janusz':'Janusz et al 2021','hott':'Hott e Menezes','samuels2001':'Samuels 2001 When',
          'mancuso':'Mancuso 2015','hoyler':'Hoyler Marques','bolognesi':'Bolognesi et al','fiva':'Fiva et al 2024',
          'samuels1999':'Samuels 1999','coxthies':'Cox and Thies 1998'}
metadata=[]
for key,prefix in prefixes.items():
    fp=next(x for x in base.iterdir() if x.name.startswith(prefix))
    with fitz.open(fp) as doc:
        pages=[page.get_text() for page in doc]
        (out/(key+'.txt')).write_text('\n\n'.join('=== PDF PAGE '+str(i+1)+' ===\n'+text for i,text in enumerate(pages)),encoding='utf-8')
        metadata.append({'chave':key,'arquivo':str(fp),'paginas':len(doc),'caracteres':sum(map(len,pages))})
(out/'fontes.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(metadata,ensure_ascii=False))
