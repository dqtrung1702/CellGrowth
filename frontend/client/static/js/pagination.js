function pagination(page,total_pages,url,elem){
    var pagination = '';
    page = Number(page);
    total_pages = Number(total_pages);
    if(page){
        var pagination = '';
        if(page > 6){
            pagination = pagination + '<a href='+url+'?page=1>First page</a>';
            pagination = pagination + '<a href='+url+'?page='+page-1+'>&laquo;</a>';
            pagination = pagination + '<a>...</a>';
        };
        for(let p=(page >= 6?page-6:1);p < page; p++  ){
            pagination = pagination + '<a href='+url+'?page='+p+'>'+p+'</a>';
        };
        pagination = pagination + '<a href='+url+'?page='+page+' class="active">'+page+'</a>';
        for(let p=page+1;p<=((page+5)<total_pages?(page+5):total_pages); p++  ){
            pagination = pagination + '<a href='+url+'?page='+p+'>'+p+'</a>';
        };
        if(page+5<total_pages){
            pagination = pagination + '<a>...</a>';
            pagination = pagination + '<a href='+url+'?page='+ (page+1) +'>&raquo;</a>'
            pagination = pagination + '<a href=' + url +'?page='+total_pages+'>Last page</a>';
        }
        document.getElementById(elem).innerHTML = pagination;            
    } else {
        document.getElementById(elem).innerHTML = null;
    }
}

function pagination2(page,total_pages,elem){
    var pagination = '';
    page = Number(page);
    total_pages = Number(total_pages);
    if(page){
        var pagination = '';
        if(page > 6){
            pagination = pagination + '<a onclick="Search(1)">First page</a>';
            pagination = pagination + '<a onclick="Search('+(page-1)+')">&laquo;</a>';
            pagination = pagination + '<a>...</a>';
        };
        for(let p=(page >= 6?page-6:1);p < page; p++  ){
            pagination = pagination + '<a onclick="Search('+p+')">'+p+'</a>';
        };
        pagination = pagination + '<a onclick="Search('+page+')" class="active">'+page+'</a>';
        for(let p=page+1;p<=((page+5)<total_pages?(page+5):total_pages); p++  ){
            pagination = pagination + '<a onclick="Search('+p+')">'+p+'</a>';
        };
        if(page+5<total_pages){
            pagination = pagination + '<a>...</a>';
            pagination = pagination + '<a onclick="Search('+(page+1)+')">&raquo;</a>'
            pagination = pagination + '<a onclick="Search('+total_pages+')">Last page</a>';
        }
        document.getElementById(elem).innerHTML = pagination;            
    } else {
        document.getElementById(elem).innerHTML = null;
    }
}