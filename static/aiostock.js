const BASE_URL = "http://127.0.0.1:5000/api";

const socket = new WebSocket('wss://ws.finnhub.io?token=c8634eiad3i9fvjhud4g');
let stocklists = []
let watchlistSymbol = document.querySelectorAll(".watchlist_symbol")
for(let x=0; x<watchlistSymbol.length; x++){
    stocklists.push(watchlistSymbol[x].innerText.toUpperCase())
}

let headerSymbol = document.querySelectorAll(".symbol")
for(let x=0; x<headerSymbol.length; x++){
    stocklists.push(headerSymbol[x].innerText.toUpperCase())
}

let different = document.querySelectorAll(".different")
    for(let x=0; x<different.length; x++){
        
        if(different[x].innerText < 0){
            different[x].classList.remove("green")
            different[x].classList.add("red")
            different[x].innerHTML = '<i class="bi bi-caret-down-fill"></i>' + different[x].innerText + "%"
            
            
        }else{
            different[x].classList.remove("red")
            different[x].classList.add("green")
            different[x].innerHTML = '<i class="bi bi-caret-up-fill"></i>' + different[x].innerText + "%"
        }
    }



socket.addEventListener('open', function (event) {
    stocklists.map(ticker =>{
        socket.send(JSON.stringify({'type':'subscribe', 'symbol': ticker}))
        })
});

// // Listen for messages
socket.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
    data = JSON.parse(event.data)
    let ticker_symbol = data["data"][0].s;
    
    let ticker_new_price = data["data"][0].p;
    
    let id_value = `${ticker_symbol.toUpperCase()}-PRICE`
    let tickerPrice = document.getElementById(id_value)
    
    if(tickerPrice){
        tickerPrice.innerText = ticker_new_price;
    }

    let header_id = `${ticker_symbol.toUpperCase()}-PRICE-header`
    let tickerPriceHeader = document.getElementById(header_id)
    tickerPriceHeader.innerText = ticker_new_price

    let header_different_id = `${ticker_symbol.toUpperCase()}-PRICE-different-header`
   
    let differentPriceHeader = document.getElementById(header_different_id)
    
    let pc = differentPriceHeader.dataset.pc
    let differentPrecent = (ticker_new_price - pc)/pc * 100
    differentPriceHeader.innerText = differentPrecent.toFixed(2)

    if(differentPriceHeader.innerText < 0){
        differentPriceHeader.classList.remove("green")
        differentPriceHeader.classList.add("red")
        differentPriceHeader.innerHTML = '<i class="bi bi-caret-down-fill"></i>' + differentPriceHeader.innerText + "%"
    }else{
        differentPriceHeader.classList.remove("red")
        differentPriceHeader.classList.add("green")
        differentPriceHeader.innerHTML = '<i class="bi bi-caret-up-fill"></i>' + differentPriceHeader.innerText + "%"
    }

    


    
});



function checkChange(){
    try {
        let cp = document.querySelector('#cp')
    let prine_change = document.querySelector('#prinechange').innerText
    if(prine_change < 0){
        
        cp.classList.add("red")
    }else{
        cp.classList.add("green")
    }

    let marketCap = document.querySelector(".market_cap")
    let marketCapNum = marketCap.innerText/1000000000
    marketCap.innerText = marketCapNum.toFixed(2) + " Bil"

    } catch (error) {
        return
    }
    

};

let mils = document.querySelectorAll(".mil")
for(let x=0; x<mils.length; x++){
    mils[x].innerText /= 1000000
}

checkChange()






