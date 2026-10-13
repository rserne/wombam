const E=require('./load-engine.js');
let max=0;
for(let g=0;g<1500;g++){
  const n=5, S=E.newGame(Array.from({length:n},(_,i)=>({name:'Naamvanveertien'.slice(0,14),ai:true,uid:'abcdefghijklmnopqrstuvwxyz12',c:i})));
  const room=()=>JSON.stringify({status:'play',host:'abcdefghijklmnopqrstuvwxyz12',seats:Array.from({length:n},(_,i)=>({id:'abcdefghijklmnopqrstuvwxyz12',name:'Naamvanveertien',ai:false})),S}).length;
  let k=0;
  while(S.phase!=='over'&&k++<5000){
    if(S.phase==='react'){ const w=E.alive(S).find(i=>E.aiNope(S,i)); if(w!=null) E.nope(S,w); else E.resolve(S); }
    else if(S.phase==='play'){ const a=E.aiChoose(S,S.cur); if(a.draw) E.draw(S,S.cur); else E.play(S,S.cur,a.cards,a); }
    else if(S.phase==='favor') E.give(S,S.favor.from,E.aiGive(S,S.favor.from));
    else E.place(S,S.cur,E.aiPlace(S,S.cur));
    max=Math.max(max,room());
  }
}
console.log('grootste spelstand:',max,'tekens');
