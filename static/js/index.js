
async function getVideosFromSearch(){
    let val = document.getElementById('input-search').value
    console.log(val,current_page)
    if(val!==title_input){
      current_page = 1
      title_input=val
    }
    console.log(val,current_page)
    fetch(`http://localhost:8000/api/v1/search/page/${current_page}?title=${title_input}`)
  .then((response) => {
    if (response.ok) {
        console.log("response received")
      return response.json();
    } else {
      throw new Error("NETWORK RESPONSE ERROR");
    }
  })
  .then(data => {
    let grid_elem = document.getElementById('video_grid')
    var dataLength = data.length;
    current_page = data[0]['Page Number']
    grid_elem.innerHTML =""
    for (var i = 1; i < dataLength; i++) {
        //console.log(data[i]);
        let div = document.createElement("div");
        //console.log(data[i].id)
        let video_id = data[i].id
        let thumbnail = data[i].snippet.thumbnails.medium.url
        let title = data[i].snippet.title
        let date = data[i].publishedAt
        //console.log(video_id,thumbnail,title,date)
        div.innerHTML = `<a href="https://www.youtube.com/watch?v=${video_id}" target="_blank">
        <img src="${thumbnail}">
        <div style="padding-left: 3px;">
            <div style="font-size: 17px;">${title}</div>
            <div style="display: flex; padding-top: 3px; color: #808080; font-size: 14px;">
              <div style="display: inline-block;">Date Published : ${date}</div>
            </div>
          </div>
        </a>`
        div.classList.add("grid_item")

        grid_elem.appendChild(div)
     }
  })
  .catch((error) => console.error("FETCH ERROR:", error));
}

let current_page=1
let title_input=""
getVideosFromSearch()

async function nextPage(){
    current_page=current_page+1
    getVideosFromSearch()
    console.log(current_page)
}

async function prevPage(){
    current_page=current_page-1
    getVideosFromSearch()
    console.log(current_page)
}
