// Haalt de spelmotor uit index.html, zodat de tests precies de code van de app gebruiken.
const fs=require('fs'), path=require('path');
const html=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const src=html.split('/* ENGINE-START */')[1].split('/* ENGINE-END */')[0];
module.exports=new Function(src+'\nreturn Engine;')();
