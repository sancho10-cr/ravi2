<script>

    function removeAllChildNodes(parent) {
        while (parent.firstChild) {
            parent.removeChild(parent.firstChild);
        }
    }
    const container=document.querySelector('#main_content');
    document.querySelector('#search_btn').addEventListener('click',(event)=>{
        container.hidden=true;
        event.preventDefault();
        const div=document.querySelector('#search_content');
        removeAllChildNodes(div);
        const child_div=document.createElement('div');
        child_div.className='row';
        const data=document.querySelector('#search_input').value.toLowerCase();
        console.log(data);
        const cols=document.querySelectorAll('.col-sm-4');
        for(const col of cols){
            const text_data=col.textContent.toLowerCase();
            if(text_data.includes(data)){
                console.log(text_data.indexOf(data));
                child_div.appendChild(col);
            }
        }
        div.appendChild(child_div);
        console.log(div);
        div.hidden=false;
        // console.log(cols_data.textContent);
    });
    document.querySelector('#search_input').addEventListener('keyup',()=>{
        const search_input=document.querySelector('#search_input').value;
        console.log(search_input)
        if (search_input.length===0){
            container.hidden=false;
            document.querySelector('#search_content').hidden=true;
            console.log('I am inside');
        }
    });
</script>