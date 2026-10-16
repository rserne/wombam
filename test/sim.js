// Gesimuleerde potjes met alleen computerspelers, plus gerichte regeltests.
const E=require('./load-engine.js');
let seed=12345;
const rand=()=>{ seed=(seed*1103515245+12345)%2147483648; return seed/2147483648; };
E.setRandom(rand);
const assert=(c,m)=>{ if(!c) throw new Error('FOUT: '+m); };

function cardsOf(S){
  const all=[...S.deck,...S.discard,...S.box];
  if(S.limbo) all.push(S.limbo);
  S.players.forEach(p=>all.push(...p.hand));
  return all;
}
function check(S,where){
  const all=cardsOf(S);
  assert(all.length===56,`${where}: ${all.length} kaarten in plaats van 56`);
  assert(new Set(all).size===56,`${where}: dubbele kaart`);
  const eks=E.ekInDeck(S)+(S.limbo?1:0);
  const alive=E.alive(S).length;
  if(S.phase!=='over') assert(eks===alive-1,`${where}: ${eks} Exploderende Wombats in het spel bij ${alive} spelers`);
  S.players.forEach(p=>{ if(p.out) assert(p.hand.length===0,`${where}: uitgeschakelde speler heeft kaarten`); });
  assert(!S.players[S.cur].out||S.phase==='over',`${where}: uitgeschakelde speler is aan de beurt`);
  assert(S.turns>=1,`${where}: beurten ${S.turns}`);
}

function playGame(n){
  const S=E.newGame(Array.from({length:n},(_,i)=>({name:'C'+i,ai:true})));
  check(S,'start');
  S.players.forEach(p=>{ assert(p.hand.length===8,'startHand'); assert(E.count(p.hand,'defuse')>=1,'geen ontmantel bij start'); });
  assert(E.ekInDeck(S)===n-1,'aantal EK bij start');
  assert(E.count(S.deck,'defuse')===Math.min(2,6-n),'extra ontmantel');
  let steps=0; const stats={plays:0,nopes:0,draws:0,booms:0,defuses:0,attacks:0,maxTurns:1};
  while(S.phase!=='over'){
    if(++steps>20000) throw new Error('spel eindigt niet');
    if(S.phase==='react'){
      const order=E.alive(S).sort(()=>rand()-0.5);
      const who=order.find(i=>E.aiNope(S,i));
      if(who!=null){ assert(E.nope(S,who),'nope mislukt'); stats.nopes++; }
      else { assert(E.resolve(S),'resolve mislukt'); stats.maxTurns=Math.max(stats.maxTurns,S.turns); }
    } else if(S.phase==='play'){
      const i=S.cur, a=E.aiChoose(S,i);
      if(a.draw){ const before=E.alive(S).length; assert(E.draw(S,i),'trekken mislukt'); stats.draws++; if(E.alive(S).length<before) stats.booms++; if(S.phase==='defuse') stats.defuses++; }
      else { assert(E.play(S,i,a.cards,a),'spelen mislukt: '+JSON.stringify(a)); stats.plays++; if(E.typeOf(a.cards[0])==='attack'&&a.cards.length===1) stats.attacks++; }
    } else if(S.phase==='favor'){
      const i=S.favor.from; assert(E.give(S,i,E.aiGive(S,i)),'geven mislukt');
    } else if(S.phase==='defuse'){
      assert(E.place(S,S.cur,E.aiPlace(S,S.cur)),'terugleggen mislukt');
    }
    check(S,'stap '+steps);
  }
  assert(S.winner!=null&&!S.players[S.winner].out,'winnaar');
  assert(E.alive(S).length===1,'precies één over');
  return {steps,...stats,winner:S.winner};
}

// ---------- gerichte regeltests ----------
function fixed(n,hands,deck){
  const S=E.newGame(Array.from({length:n},(_,i)=>({name:'P'+i,ai:false})));
  // alles terug in de doos en de stand zelf neerzetten
  const pool=cardsOf(S); const take=t=>{ const c=pool.find(x=>E.typeOf(x)===t); pool.splice(pool.indexOf(c),1); return c; };
  S.players.forEach((p,i)=>{ p.hand=(hands[i]||[]).map(take); });
  S.deck=deck.map(take); S.discard=[]; S.limbo=null; S.box=pool; S.cur=0; S.turns=1; S.stacked=false; S.phase='play';
  return S;
}
const tests={
  'aanval: volgende speler 2 beurten'(){
    const S=fixed(3,[['attack'],[],[]],['taco','taco','taco','ek','ek']);
    E.play(S,0,[S.players[0].hand[0]]); E.resolve(S);
    assert(S.cur===1&&S.turns===2,'cur '+S.cur+' turns '+S.turns);
    E.draw(S,1); assert(S.cur===1&&S.turns===1,'na eerste trekbeurt'); E.draw(S,1); assert(S.cur===2&&S.turns===1,'na tweede');
  },
  'aanval stapelt: aangevallen speler valt aan → 4 beurten'(){
    const S=fixed(3,[['attack'],['attack'],[]],['taco','taco','taco','ek','ek']);
    E.play(S,0,[S.players[0].hand[0]]); E.resolve(S);
    E.play(S,1,[S.players[1].hand[0]]); E.resolve(S);
    assert(S.cur===2&&S.turns===4,'turns '+S.turns);
  },
  'sla over bij aanval beëindigt één beurt'(){
    const S=fixed(3,[['attack'],['skip'],[]],['taco','taco','ek','ek']);
    E.play(S,0,[S.players[0].hand[0]]); E.resolve(S);
    E.play(S,1,[S.players[1].hand[0]]); E.resolve(S);
    assert(S.cur===1&&S.turns===1,'cur '+S.cur+' turns '+S.turns);
  },
  'nope houdt actie tegen, nope op nope laat hem doorgaan'(){
    const S=fixed(3,[['attack','nope'],['nope'],[]],['taco','ek','ek']);
    const a=S.players[0].hand.find(c=>E.typeOf(c)==='attack');
    E.play(S,0,[a]);
    assert(!E.canNope(S,0),'eigen actie niet tegenhouden');
    assert(E.nope(S,1),'nope'); assert(!E.canNope(S,1),'niet twee keer achter elkaar');
    assert(E.nope(S,0),'nope op nope'); E.resolve(S);
    assert(S.cur===1&&S.turns===2,'aanval ging door');
    const S2=fixed(2,[['skip'],['nope']],['taco','ek']);
    E.play(S2,0,[S2.players[0].hand[0]]); E.nope(S2,1); E.resolve(S2);
    assert(S2.cur===0&&S2.turns===1,'sla over tegengehouden');
  },
  'ontmantelen en geheim terugleggen'(){
    const S=fixed(2,[['defuse'],['taco']],['ek','taco','taco']);
    E.draw(S,0); assert(S.phase==='defuse'&&S.players[0].hand.length===0,'ontmantel');
    E.place(S,0,1); assert(E.typeOf(S.deck[1])==='ek'&&S.cur===1&&S.phase==='play','teruggelegd op plek 2');
    assert(S.discard.some(c=>E.typeOf(c)==='defuse'),'ontmantel op aflegstapel');
  },
  'ontploffen zonder ontmantel, laatste speler wint'(){
    const S=fixed(2,[['taco'],['taco']],['ek','taco']);
    E.draw(S,0); assert(S.players[0].out&&S.phase==='over'&&S.winner===1,'ontploft');
  },
  'kateautje: tegenstander kiest de kaart'(){
    const S=fixed(2,[['favor'],['nope','taco']],['taco','ek']);
    E.play(S,0,[S.players[0].hand[0]],{target:1}); E.resolve(S);
    assert(S.phase==='favor'&&E.needs(S)===1,'favor fase');
    const c=S.players[1].hand.find(x=>E.typeOf(x)==='taco'); E.give(S,1,c);
    assert(S.players[0].hand.includes(c)&&S.phase==='play'&&S.cur===0,'gekregen, beurt gaat door');
  },
  'paar steelt willekeurige kaart, drietal eist genoemde kaart'(){
    const S=fixed(2,[['taco','taco','melon','melon','melon'],['defuse','skip']],['taco','ek']);
    const tacos=S.players[0].hand.filter(c=>E.typeOf(c)==='taco');
    E.play(S,0,tacos,{target:1}); E.resolve(S);
    assert(S.players[0].hand.length===4&&S.players[1].hand.length===1,'gestolen');
    const melons=S.players[0].hand.filter(c=>E.typeOf(c)==='melon');
    const had=E.typeOf(S.players[1].hand[0]);
    E.play(S,0,melons,{target:1,named:had}); E.resolve(S);
    assert(S.players[1].hand.length===0&&S.players[0].hand.length===2,'opgeëist');
  },
  'elk paar van dezelfde kaart telt, ook actiekaarten'(){
    const S=fixed(2,[['skip','skip'],['taco']],['taco','ek']);
    assert(E.canPlay(S,0,S.players[0].hand,{target:1}),'paar sla over');
  },
  'voorspel: bovenste drie kaarten privé'(){
    const S=fixed(2,[['future'],['taco']],['taco','ek','melon','beard']);
    E.play(S,0,[S.players[0].hand[0]]); E.resolve(S);
    const ib=S.players[0].inbox.at(-1);
    assert(ib.kind==='see'&&ib.cards.map(E.typeOf).join()==='taco,ek,melon','gezien');
    assert(!S.players[1].inbox.some(x=>x.kind==='see'),'ander ziet niets');
  },
  'opbouw bij 2, 3, 4 en 5 spelers'(){
    for(const n of [2,3,4,5]){
      const S=E.newGame(Array.from({length:n},(_,i)=>({name:'x'+i})));
      check(S,'opbouw '+n);
      assert(S.deck.length===46-7*n+Math.min(2,6-n)+n-1,'stapelgrootte '+n);
    }
  }
};
let ok=0;
for(const [name,fn] of Object.entries(tests)){ fn(); ok++; console.log('✓',name); }

const agg={games:0,steps:0,plays:0,nopes:0,draws:0,booms:0,defuses:0,attacks:0,maxTurns:0}, wins={};
for(const n of [2,3,4,5]) for(let g=0;g<500;g++){
  const r=playGame(n); agg.games++;
  for(const k of ['steps','plays','nopes','draws','booms','defuses','attacks']) agg[k]+=r[k];
  agg.maxTurns=Math.max(agg.maxTurns,r.maxTurns);
  wins[n+'p seat'+r.winner]=(wins[n+'p seat'+r.winner]||0)+1;
}
console.log(`\n${ok} regeltests geslaagd. ${agg.games} potjes gesimuleerd zonder fouten of zoekgeraakte kaarten.`);
console.log(`Gemiddeld per potje: ${(agg.steps/agg.games).toFixed(0)} stappen, ${(agg.plays/agg.games).toFixed(1)} gespeelde kaarten, ${(agg.nopes/agg.games).toFixed(1)} keer Nope, ${(agg.defuses/agg.games).toFixed(1)} keer ontmanteld. Hoogste aantal beurten na stapelen: ${agg.maxTurns}.`);
console.log(wins);
