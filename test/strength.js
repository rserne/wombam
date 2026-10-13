// Hoe sterk is de computerspeler? Slimme speler tegen spelers die alleen trekken of willekeurig spelen.
const E=require('./load-engine.js');
let seed=777; const rand=()=>{ seed=(seed*1103515245+12345)%2147483648; return seed/2147483648; }; E.setRandom(rand);
function naive(S,i){ // speelt willekeurig een losse actiekaart (30%), anders trekken
  const h=S.players[i].hand, acts=h.filter(c=>['skip','attack','shuffle','future'].includes(E.typeOf(c)));
  if(acts.length&&rand()<0.3) return {cards:[acts[Math.floor(rand()*acts.length)]]};
  return {draw:true};
}
let wins=0, games=3000, n=3;
for(let g=0;g<games;g++){
  const S=E.newGame(Array.from({length:n},(_,i)=>({name:'p'+i,ai:true})));
  const smart=g%n; let guard=0;
  while(S.phase!=='over'&&guard++<20000){
    if(S.phase==='react'){ const w=E.alive(S).find(i=>i===smart&&E.aiNope(S,i)); if(w!=null) E.nope(S,w); else E.resolve(S); }
    else if(S.phase==='play'){ const i=S.cur, a=i===smart?E.aiChoose(S,i):naive(S,i); if(a.draw) E.draw(S,i); else E.play(S,i,a.cards,a); }
    else if(S.phase==='favor') E.give(S,S.favor.from,E.aiGive(S,S.favor.from));
    else if(S.phase==='defuse') E.place(S,S.cur,S.cur===smart?E.aiPlace(S,S.cur):Math.floor(rand()*(S.deck.length+1)));
  }
  if(S.winner===smart) wins++;
}
console.log(`Slimme computerspeler wint ${(100*wins/games).toFixed(1)}% van ${games} potjes met ${n} spelers (bij toeval ${(100/n).toFixed(1)}%).`);
