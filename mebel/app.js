const U=(id,w=1200)=>`https://images.unsplash.com/${id}?w=${w}&q=75&auto=format&fit=crop`;
const PHONE='+7 (812) 000-00-00',TEL='+78120000000';
const fmt=n=>Math.round(n).toLocaleString('ru-RU')+' ₽';

const I={
  arrow:'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M7 17L17 7M9 7h8v8"/></svg>',
  phone:'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
  wa:'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21l1.6-4.6A9 9 0 1 1 8 19.5z"/></svg>',
  vk:'<svg class="ico" viewBox="0 0 24 24" fill="currentColor"><path d="M12.8 17.5c-5.5 0-8.6-3.8-8.7-10h2.8c.1 4.6 2.1 6.5 3.7 6.9V7.5h2.6v3.9c1.6-.2 3.3-2 3.8-3.9h2.6a7.7 7.7 0 0 1-3.5 5 7.9 7.9 0 0 1 4.1 5h-2.9a5 5 0 0 0-4.1-3.6v3.6z"/></svg>'
};

const WORKS=[
 {id:1,type:'kitchen',t:'Кухня',name:'Кухня «Графит и дуб»',img:'photo-1632583824020-937ae9564495',gal:['photo-1622372738946-62e02505feb3','photo-1600684388091-627109f3cd60','photo-1778731660397-6a66493be391'],place:'Приморский район',size:'Угловая, 3,6 м',mat:'МДФ эмаль, шпон дуба, кварц',price:386000,days:21,
  task:'Квартира в новостройке, кухня-гостиная 22 м². Хозяева хотели тёмную кухню, которая не «съест» свет, и много мест для хранения без верхних шкафов у окна.',
  sol:'Нижний ряд — матовая графитовая эмаль, пенал и полки — шпон дуба. Кварцевая столешница 12 мм, интегрированные ручки, подсветка рабочей зоны.',
  res:'Кухню изготовили за 21 день, монтаж занял 2 дня. Вошла встроенная техника, посудомойка 60 см и колонна под духовку на уровне глаз.'},
 {id:2,type:'kitchen',t:'Кухня',name:'Кухня с островом «Тёмный лес»',img:'photo-1622372738946-62e02505feb3',gal:['photo-1632583824020-937ae9564495','photo-1778731660397-6a66493be391'],place:'Курортный район, частный дом',size:'Прямая 4,2 м + остров',mat:'МДФ эмаль, керамика',price:512000,days:28,
  task:'Большая кухня в доме, где готовят каждый день и часто принимают гостей.',sol:'Прямая кухня во всю стену и остров с варочной панелью и барной зоной на 4 места.',res:'Остров стал центром дома: готовят и общаются одновременно.'},
 {id:3,type:'kitchen',t:'Кухня',name:'Кухня «Синий акцент»',img:'photo-1588854337236-6889d631faa8',gal:['photo-1588854337221-4cf9fa96059c'],place:'Московский район',size:'Угловая, 3,1 м',mat:'МДФ эмаль, акрил',price:298000,days:20,
  task:'Яркая кухня в квартире вторичного фонда с неровными стенами.',sol:'Сняли точные размеры лазером, учли перепады стен в проекте, добавили дополнительную планку.',res:'Ни одного зазора, фасады встали идеально ровно.'},
 {id:4,type:'kitchen',t:'Кухня',name:'Кухня «Светлый скандинав»',img:'photo-1602028915047-37269d1a73f7',gal:['photo-1556912167-f556f1f39fdf','photo-1556912173-46c336c7fd55'],place:'Красногвардейский район',size:'Прямая 3,8 м + остров',mat:'МДФ плёнка, ЛДСП Egger',price:274000,days:18,
  task:'Светлая и практичная кухня для семьи с детьми.',sol:'Фасады в матовой плёнке, которая не боится царапин, остров с ящиками для хранения.',res:'Уложились в бюджет, не потеряв в качестве.'},
 {id:5,type:'kitchen',t:'Кухня',name:'Кухня «Мрамор»',img:'photo-1785535573585-8f962fa3cda5',gal:['photo-1602028915047-37269d1a73f7'],place:'Петроградский район',size:'П-образная, 5,4 м',mat:'МДФ эмаль, кварц под мрамор',price:455000,days:25,
  task:'Кухня в квартире с высокими потолками 3,2 м.',sol:'Шкафы до потолка в два ряда, кварц с мраморным рисунком, подсветка в цоколе.',res:'Хранения стало в 2 раза больше, чем было.'},
 {id:6,type:'kitchen',t:'Кухня',name:'Кухня «Белая классика»',img:'photo-1484154218962-a197022b5858',gal:['photo-1507089947368-19c1da9775ae','photo-1556911220-bff31c812dba'],place:'Выборгский район',size:'Угловая, 3,0 м',mat:'МДФ плёнка, ЛДСП',price:168000,days:14,
  task:'Недорогая кухня для сдачи квартиры в аренду.',sol:'Надёжная ЛДСП, плёночные фасады и фурнитура Hettich.',res:'Кухня за 14 дней и в рамках бюджета.'},
 {id:7,type:'wardrobe',t:'Шкаф',name:'Шкаф-купе с зеркалом',img:'photo-1672137233327-37b0c1049e77',gal:['photo-1631048499455-4f9e26f23b9f'],place:'Невский район',size:'2,8 × 2,7 м',mat:'ЛДСП Egger, зеркало, профиль Raumplus',price:96000,days:12,
  task:'Шкаф в спальню до потолка с зеркалом.',sol:'Купе с тремя дверями, внутри — штанги, полки и выдвижные ящики.',res:'Вместил вещи всей семьи, комната визуально стала больше.'},
 {id:8,type:'closet',t:'Гардеробная',name:'Гардеробная «Бутик»',img:'photo-1618236444721-4a8dba415c15',gal:['photo-1631048499455-4f9e26f23b9f'],place:'Центральный район',size:'2,4 × 2,1 м',mat:'ЛДСП, стекло, подсветка',price:142000,days:16,
  task:'Гардеробная как в магазине: всё на виду.',sol:'Открытые стеллажи, стеклянные ящики, подсветка в каждой секции.',res:'Сборы по утрам стали в разы быстрее.'},
 {id:9,type:'closet',t:'Гардеробная',name:'Белая гардеробная',img:'photo-1687953413905-731f620177ae',gal:['photo-1631048834949-85e003d913c9'],place:'Калининский район',size:'1,8 × 1,6 м',mat:'ЛДСП белый, металл',price:88000,days:12,
  task:'Маленькая кладовка 3 м².',sol:'Г-образное наполнение, двойные штанги, полки для обуви.',res:'Кладовка превратилась в полноценную гардеробную.'},
 {id:10,type:'wardrobe',t:'Шкаф',name:'Встроенный шкаф в коридор',img:'photo-1631048834949-85e003d913c9',gal:['photo-1672137233327-37b0c1049e77'],place:'Фрунзенский район',size:'2,2 × 2,6 м',mat:'МДФ эмаль',price:74000,days:10,
  task:'Шкаф в узкий коридор.',sol:'Распашные двери без ручек, глубина 45 см.',res:'Коридор не стал теснее, а места для вещей хватает.'},
 {id:11,type:'hall',t:'Прихожая',name:'Прихожая со встроенным шкафом',img:'photo-1635108197511-8e6046f191f3',gal:['photo-1600494448868-9fbd1ac2d9f5'],place:'Приморский район',size:'3,0 м',mat:'МДФ плёнка, ЛДСП',price:64000,days:10,
  task:'Прихожая с банкеткой и местом для обуви.',sol:'Шкаф с антресолью, открытая ниша с крючками и банкетка.',res:'У каждой вещи своё место.'},
 {id:12,type:'hall',t:'Прихожая',name:'Прихожая «Минимализм»',img:'photo-1790926154776-faa3ff0d6b2a',gal:['photo-1635108198077-4f849708645b'],place:'Василеостровский район',size:'2,4 м',mat:'МДФ эмаль',price:58000,days:9,
  task:'Минималистичная прихожая без лишних деталей.',sol:'Шкаф заподлицо со стеной, скрытые ручки.',res:'Шкаф почти не заметен, но вмещает всё.'}
];

function shell(active){
  const links=[['index.html','Главная'],['works.html','Наши работы'],['calc.html','Калькулятор'],['production.html','Производство'],['index.html#contacts','Контакты']];
  document.body.insertAdjacentHTML('afterbegin',`<div class="demo">Демо-проект для портфолио: компания «Фасад» вымышленная, фото — Unsplash, цены ориентировочные</div>
<header><div class="wrap nav">
  <a class="logo" href="index.html"><i>Ф</i><span>ФАСАД<small>мебель на заказ · СПб</small></span></a>
  <nav class="menu" id="menu">${links.map(l=>`<a href="${l[0]}" class="${l[1]===active?'on':''}">${l[1]}</a>`).join('')}</nav>
  <div class="hdr-r"><a class="ph" href="tel:${TEL}">${PHONE}<small>ежедневно 9:00–21:00</small></a><a class="btn btn-oak" href="calc.html">Рассчитать стоимость</a>
  <button class="burger" aria-label="Меню" onclick="document.getElementById('menu').classList.toggle('open')"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button></div>
</div></header>`);
  document.body.insertAdjacentHTML('beforeend',`<footer><div class="wrap">
  <div class="fgrid">
    <div><a class="logo" href="index.html" style="color:#fff"><i>Ф</i><span>ФАСАД<small>мебель на заказ · СПб</small></span></a><p style="margin-top:18px;font-size:14.5px;max-width:320px">Кухни, шкафы и гардеробные по индивидуальным размерам. Собственное производство в Санкт-Петербурге.</p></div>
    <div><h4>Мебель</h4><ul><li><a href="works.html?f=kitchen">Кухни</a></li><li><a href="works.html?f=wardrobe">Шкафы-купе</a></li><li><a href="works.html?f=closet">Гардеробные</a></li><li><a href="works.html?f=hall">Прихожие</a></li></ul></div>
    <div><h4>Компания</h4><ul><li><a href="works.html">Наши работы</a></li><li><a href="production.html">Производство</a></li><li><a href="calc.html">Калькулятор</a></li><li><a href="index.html#faq">Вопросы</a></li></ul></div>
    <div><h4>Контакты</h4><ul><li><a href="tel:${TEL}">${PHONE}</a></li><li>WhatsApp · ВКонтакте</li><li>Санкт-Петербург, производство в Шушарах</li><li>Ежедневно 9:00–21:00</li></ul></div>
  </div>
  <div class="fbot"><span>© «Фасад», 2026 · демо-проект, компания вымышленная</span><span>Сайт: Леонтий · leonti123.github.io</span></div>
</div></footer>
<div class="fab"><a class="wa" href="#" aria-label="WhatsApp" onclick="return false">${I.wa.replace('class="ico"','width="26" height="26" style="color:#fff"')}</a><a class="tl" href="tel:${TEL}" aria-label="Позвонить">${I.phone.replace('class="ico"','width="24" height="24" style="color:#fff"')}</a></div>`);
  document.querySelectorAll('form.lead-form').forEach(f=>f.onsubmit=e=>{e.preventDefault();f.innerHTML='<h3 style="font-size:24px">Спасибо! Заявка принята</h3><p style="margin-top:10px;color:#cfc6bb">Это демо-сайт. На рабочем сайте заявка сразу придёт менеджеру во ВКонтакте, WhatsApp или на почту, и он перезвонит в течение 15 минут.</p>'});
}

function workCard(w){return `<a class="work" href="case.html?id=${w.id}"><div class="im"><img src="${U(w.img,800)}" alt="${w.name}" loading="lazy"></div><div class="b"><span class="t">${w.t} · ${w.place}</span><h3>${w.name}</h3><div class="m">${w.size} · ${w.mat}</div><div class="p"><span>${w.days} дней</span><b>${fmt(w.price)}</b></div></div></a>`}

function renderWorks(el,filter,limit){
  const list=WORKS.filter(w=>filter==='all'||w.type===filter);
  el.innerHTML=(limit?list.slice(0,limit):list).map(workCard).join('');
}

function initFilters(){
  const el=document.getElementById('works');const btns=document.querySelectorAll('.filters button');
  const f=new URLSearchParams(location.search).get('f')||'all';
  const set=v=>{btns.forEach(b=>b.classList.toggle('on',b.dataset.f===v));renderWorks(el,v)};
  btns.forEach(b=>b.onclick=()=>set(b.dataset.f));set(f);
}

function initCase(){
  const id=+new URLSearchParams(location.search).get('id')||1;const w=WORKS.find(x=>x.id===id)||WORKS[0];
  document.title=w.name+' — «Фасад», мебель на заказ в СПб';
  const imgs=[w.img,...w.gal];
  document.getElementById('case').innerHTML=`
  <div class="crumbs"><a href="index.html">Главная</a> / <a href="works.html">Наши работы</a> / ${w.name}</div>
  <h1 style="font-size:clamp(30px,4vw,52px);margin-bottom:28px">${w.name}</h1>
  <div class="case-top">
    <div class="gal">${imgs.map(i=>`<img src="${U(i,1400)}" alt="${w.name}" data-full="${U(i,2000)}">`).join('')}</div>
    <aside class="spec"><span class="kicker">${w.t}</span><div class="price">${fmt(w.price)}</div>
      <dl><dt>Район</dt><dd>${w.place}</dd><dt>Размеры</dt><dd>${w.size}</dd><dt>Материалы</dt><dd>${w.mat}</dd><dt>Изготовление</dt><dd>${w.days} дней</dd><dt>Гарантия</dt><dd>3 года</dd></dl>
      <a class="btn btn-oak" style="width:100%" href="calc.html">Рассчитать похожую</a>
      <a class="btn btn-line" style="width:100%;margin-top:10px" href="index.html#contacts">Вызвать замерщика</a></aside>
  </div>
  <div class="story"><div><b>Задача</b><p>${w.task}</p></div><div><b>Решение</b><p>${w.sol}</p></div><div><b>Результат</b><p>${w.res}</p></div></div>`;
  const others=WORKS.filter(x=>x.type===w.type&&x.id!==w.id).concat(WORKS.filter(x=>x.type!==w.type)).slice(0,3);
  document.getElementById('more').innerHTML=others.map(workCard).join('');
  const lb=document.getElementById('lb');document.querySelectorAll('.gal img').forEach(i=>i.onclick=()=>{lb.querySelector('img').src=i.dataset.full;lb.classList.add('on')});lb.onclick=()=>lb.classList.remove('on');
}

function initCalc(){
  const st={kind:'kitchen',shape:'corner',len:3.5,fac:48000,top:20000,ex:{}};
  const W={type:'coupe',wid:2.5,ceil:false,mirror:true,light:false};
  const $=s=>document.querySelector(s);
  document.querySelectorAll('[data-g]').forEach(o=>o.onclick=()=>{const g=o.dataset.g;document.querySelectorAll(`[data-g="${g}"]`).forEach(x=>x.classList.toggle('on',x===o));const v=o.dataset.v;if(g==='shape')st.shape=v;if(g==='fac')st.fac=+v;if(g==='top')st.top=+v;if(g==='wtype')W.type=v;calc()});
  $('#len').oninput=e=>{st.len=+e.target.value;calc()};
  $('#wid').oninput=e=>{W.wid=+e.target.value;calc()};
  document.querySelectorAll('[data-ex]').forEach(c=>c.onchange=()=>{st.ex[c.dataset.ex]=c.checked;calc()});
  document.querySelectorAll('[data-wx]').forEach(c=>c.onchange=()=>{W[c.dataset.wx]=c.checked;calc()});
  document.querySelectorAll('.tabs2 button').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tabs2 button').forEach(x=>x.classList.toggle('on',x===b));st.kind=b.dataset.k;$('#kKitchen').style.display=st.kind==='kitchen'?'':'none';$('#kWard').style.display=st.kind==='ward'?'':'none';calc()});
  function calc(){
    let rows=[],sum=0;
    if(st.kind==='kitchen'){
      $('#lenv').textContent=st.len.toLocaleString('ru-RU')+' м';
      const shapeK={line:1,corner:1.12,u:1.2,island:1}[st.shape];
      const base=st.len*st.fac*shapeK;rows.push(['Корпуса и фасады',base]);
      const extra={line:0,corner:15000,u:30000,island:90000}[st.shape];if(extra)rows.push([{corner:'Угловой модуль',u:'Два угловых модуля',island:'Остров'}[st.shape],extra]);
      rows.push(['Столешница',st.len*st.top]);
      if(st.ex.blum)rows.push(['Фурнитура Blum с доводчиками',base*.06]);
      if(st.ex.ceil)rows.push(['Верхний ряд до потолка',base*.15]);
      if(st.ex.light)rows.push(['Подсветка рабочей зоны',14000]);
      if(st.ex.tech)rows.push(['Встраивание техники',12000]);
      rows.push(['Доставка, подъём и монтаж',Math.max(12000,st.len*4000)]);
      $('#rtitle').textContent='Кухня';
    }else{
      $('#widv').textContent=W.wid.toLocaleString('ru-RU')+' м';
      const per={coupe:18000,swing:22000,closet:28000}[W.type];let base=W.wid*per;if(W.ceil)base*=1.1;
      rows.push([{coupe:'Шкаф-купе',swing:'Распашной шкаф',closet:'Гардеробная система'}[W.type],base]);
      if(W.mirror&&W.type!=='closet')rows.push(['Зеркальные двери',W.wid*4000]);
      if(W.light)rows.push(['Подсветка',8000]);
      rows.push(['Доставка и монтаж',Math.max(6000,W.wid*2000)]);
      $('#rtitle').textContent='Шкаф или гардеробная';
    }
    sum=rows.reduce((a,r)=>a+r[1],0);
    const lo=Math.round(sum*.92/1000)*1000,hi=Math.round(sum*1.08/1000)*1000;
    $('#sum').textContent=lo.toLocaleString('ru-RU')+' – '+fmt(hi);
    $('#rows').innerHTML=rows.map(r=>`<li><span>${r[0]}</span><span>${fmt(Math.round(r[1]/100)*100)}</span></li>`).join('');
  }
  calc();
}
