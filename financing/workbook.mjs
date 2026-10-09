// Python's shared layout plan owns data and formulas. Preview/export are separate.
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
let input='';for await(const chunk of process.stdin) input+=chunk;
const {plan}=JSON.parse(input);
const wb=Workbook.create();
for(const spec of plan) wb.worksheets.add(spec.name);
for(const spec of plan){
  const sh=wb.worksheets.getItem(spec.name);sh.showGridLines=false;
  const columns=Math.max(...spec.rows.map(r=>r.length));
  const matrix=spec.rows.map(r=>r.concat(Array(columns-r.length).fill(null)));
  sh.getRangeByIndexes(1,0,matrix.length,columns).values=matrix;
  const area=sh.getUsedRange();area.format.font.name='Arial';area.format.font.size=11;
  area.format.font.color='#172C43';area.format.wrapText=true;area.format.verticalAlignment='center';
  area.format.rowHeight=spec.name==='Historical gap review'?150:spec.name==='Historical assumptions'?210:spec.name.startsWith('Historical')||spec.name==='Funding unit sensitivities'?80:spec.name==='Evidence'?90:spec.name==='Summary'?50:spec.name==='Contents'?48:36;
  if(spec.name.startsWith('Public')) area.format.rowHeight=spec.name==='Public gap assessment'?130:spec.name==='Public output policy'||spec.name==='Public conventions'?100:60;
  for(let j=0;j<columns;j++) sh.getRangeByIndexes(1,j,matrix.length,1).format.columnWidth=spec.widths[j]??20;
  sh.getRangeByIndexes(1,0,1,columns).format.font.bold=true;
  if(spec.header_row){
    sh.getRangeByIndexes(1,0,1,Math.min(columns,6)).merge();
    sh.getRangeByIndexes(2,0,1,Math.min(columns,6)).merge();
    sh.getRangeByIndexes(1,0,2,columns).format.rowHeight=42;
    const h=sh.getRangeByIndexes(spec.header_row-1,0,1,columns);
    h.format.fill='#203D5B';h.format.font.color='#FFFFFF';h.format.rowHeight=42;
    sh.freezePanes.freezeRows(spec.header_row);
    if(spec.name!=='Evidence'&&spec.name!=='Sources'){
      sh.getRangeByIndexes(spec.header_row,0,Math.max(1,matrix.length+1-spec.header_row),columns).setNumberFormat('#,##0.0;(#,##0.0);"-"');
    }
  }
  for(const f of spec.number_formats??[]) sh.getRangeByIndexes(spec.header_row,f.column,Math.max(1,matrix.length+1-spec.header_row),1).setNumberFormat(f.format);
  if(spec.name.includes('assumptions')||spec.name==='Assumptions') sh.getRangeByIndexes(spec.header_row,0,Math.max(1,matrix.length+1-spec.header_row),columns).format.font.color='#1768a6';
  for(const f of spec.formulas){sh.getRange(f.cell).formulas=[[f.formula]];sh.getRange(f.cell).format.font.color='#08754e';}
  if(spec.name==='Summary') sh.getRange('B3').conditionalFormats.add('containsText',{text:'Blocked',format:{fill:'#FFF1EE',font:{color:'#B42318',bold:true}}});
}
wb.recalculate();
console.error((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:20},summary:'Final workbook formula error scan'})).ndjson);
if(process.env.FINANCING_PREVIEW_DIR){
  await fs.mkdir(process.env.FINANCING_PREVIEW_DIR,{recursive:true});
  for(const spec of plan){
    const range=spec.name==='Summary'?'A1:B12':spec.name==='Evidence'?'A1:D7':spec.name==='Assumptions'?'A1:B9':spec.name==='Sources'?'A1:D8':'A1:F9';
    const blob=await wb.render({sheetName:spec.name,range,scale:1,format:'png'});
    await fs.writeFile(path.join(process.env.FINANCING_PREVIEW_DIR,spec.name+'.png'),new Uint8Array(await blob.arrayBuffer()));
  }
  process.exit(0);
}
const target=process.argv[2];await fs.mkdir(path.dirname(target),{recursive:true});
await (await SpreadsheetFile.exportXlsx(wb)).save(target);
process.exit(0);
