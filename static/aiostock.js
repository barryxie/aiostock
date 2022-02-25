const BASE_URL = "http://127.0.0.1:5000/api";





function checkChange(){
    try {
        let cp = document.querySelector('#cp')
    let prine_change = document.querySelector('#prinechange').innerText
    if(prine_change < 0){
        
        cp.classList.add("red")
    }else{
        cp.classList.add("green")
    }
    } catch (error) {
        return
    }
    

};


async function getheader(){
    let headdisplay = document.querySelector(".headdisplay")
    const res = await axios.get(`${BASE_URL}/header`)
    let tickers = res.data
    
    

    const socket = new WebSocket('wss://ws.finnhub.io?token=c8634eiad3i9fvjhud4g');

// Connection opened -> Subscribe
    socket.addEventListener('open', function (event) {
    for(let x=0; x < tickers.length; x++ ){
        let col = document.createElement("div")
        col.classList.add('col')
        col.setAttribute('id',`symboldiv-${x}`)
        let row = document.createElement("div")
            row.classList.add('row')
            let symboldiv = document.createElement("div")
                symboldiv.classList.add('col', 'symbol')
                symboldiv.setAttribute('id',`symbol-${x}`)
                symboldiv.innerText=tickers[x]["symbol"]
                row.append(symboldiv)
             let pricediv = document.createElement("div")
                pricediv.classList.add('col', 'price')
                pricediv.setAttribute('id',`price-${x}`)
                pricediv.innerText = tickers[x]["data"]["c"]
                row.append(pricediv)
        col.append(row)
        let differentdiv = document.createElement("div") 
            differentdiv.classList.add('different')
            differentdiv.setAttribute('id',`different-${x}`)  
            differentNumber = (pricediv.innerText - tickers[x]["data"]["pc"])/tickers[x]["data"]["pc"] * 100
            differentdiv.innerText = differentNumber.toFixed(2) +"%"
        col.append(differentdiv)

    headdisplay.append(col)
    col = document.querySelector(`#symboldiv-${x}`)
            if(differentNumber < 0){
                differentdiv.classList.remove("green")
                differentdiv.classList.add("red")
                
            }else{
                differentdiv.classList.remove("red")
                differentdiv.classList.add("green")
            }
    socket.send(JSON.stringify({'type':'subscribe', 'symbol': tickers[x]["symbol"] }))
    }
    
});

    socket.addEventListener('message', function (e) {
        data = JSON.parse(e.data)
        for(let x=0; x < tickers.length; x++ ){
            let symbol = document.querySelector(`#symbol-${[x]}`)
            let price = document.querySelector(`#price-${[x]}`)
            let different = document.querySelector(`#different-${[x]}`)
            symbol.innerText=tickers[x]["symbol"]
            try {
                if(data["data"][0]["s"] === tickers[x]["symbol"]){
                    price.innerText = data["data"][0]["p"]
                }
    
            } catch (error) {
                
            }
            
            differentNumber = (price.innerText - tickers[x]["data"]["pc"])/tickers[x]["data"]["pc"] * 100
            different.innerText = differentNumber.toFixed(2) +"%"

            // col = document.querySelector(`#symboldiv-${x}`)
            // if(differentNumber < 0){
            //     col.classList.remove("green-bg")
            //     col.classList.add("red-bg")
                
            // }else{
            //     col.classList.remove("red-bg")
            //     col.classList.add("green-bg")
            // }

        }
    });
}

getheader()
checkChange()






