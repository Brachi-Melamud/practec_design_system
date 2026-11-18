const menuButton=document.querySelector('.menu-btn');
const navLinks=document.querySelector('.nav-links');
menuButton?.addEventListener('click',()=>{
  const open=menuButton.getAttribute('aria-expanded')==='true';
  menuButton.setAttribute('aria-expanded',String(!open));
  navLinks?.classList.toggle('open',!open);
});
navLinks?.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{
  menuButton?.setAttribute('aria-expanded','false');
  navLinks.classList.remove('open');
}));
document.querySelector('#applyForm')?.addEventListener('submit',(event)=>{
  event.preventDefault();
  const button=event.currentTarget.querySelector('button');
  button.innerHTML='הפרטים נשלחו בהצלחה ✓';
  button.disabled=true;
});
