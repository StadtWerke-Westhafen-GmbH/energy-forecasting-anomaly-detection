const demo = window.SWW.demo();
window.SWW.GALLERY.forEach((definition,index)=>{
  const section=document.createElement('section'); section.className='chart-card';
  const header=document.createElement('header'); const heading=document.createElement('h2');
  heading.textContent=String(index+1).padStart(2,'0')+' · '+definition.title;
  const caption=document.createElement('p'); caption.textContent=definition.when;
  header.append(heading,caption); const chart=document.createElement('div'); chart.className='chart';
  chart.setAttribute('role','img'); chart.setAttribute('aria-label',definition.title+' – synthetisches Beispiel');
  section.append(header,chart); document.getElementById('gallery').append(section);
  window.SWW.render(chart,definition.build(demo));
});
