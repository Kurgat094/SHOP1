document.addEventListener('DOMContentLoaded',function(){
    const cards =document.querySelectorAll('.card');
    const prevBtn=document.querySelectorAll('.prev');
    const nextBtn=document.querySelectorAll('.next');
    let currentPage=0;
    const cardspage=2;
    
    showPage(currentPage);

    prevBtn.addEventListener('click',() => {
        if (currentPage>0){
            currentPage--;
            showPage(currentPage);

        }
    });
    nextBtn.addEventListener('click',() => {
        if ( currentPage< Math.ceil(cards.length/ cardsPerPage) -1){
            currentPage++;
            showPage(currentPage);
        }
    });
    function showPage(page){
        const startIndex =page*cardsPerPage;
        const endIndex =startIndex + currentPage;

        cards.forEach((card,index)=>{
            if (index >= startIndex && index < endIndex) {
                card.style.display='block';
            } else {
                card.style.display='none';
            }
        });
    }
});