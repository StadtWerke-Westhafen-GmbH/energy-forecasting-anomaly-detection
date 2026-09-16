const types=['Title','Agenda','Section','Kpi','Chart','Comparison','MlCanvas','Table','Quote','Closing'];
for(const type of types){
 const container=document.createElement('div');container.className='slide-wrapper';
 const frame=document.createElement('iframe');frame.src=`../../slides/${type}Slide.html`;frame.title=`${type} – Layoutbeispiel`;frame.loading='lazy';
 container.append(frame);document.getElementById('slides').append(container);
 new ResizeObserver(()=>{const scale=container.clientWidth/1280;frame.style.transform=`scale(${scale})`;container.style.height=`${720*scale}px`;}).observe(container);
}
