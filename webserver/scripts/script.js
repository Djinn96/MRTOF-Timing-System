
const SERVER_ADDR = "http://202.13.199.181:8000"

async function httpRequest(path,method,body) {
    return await fetch(SERVER_ADDR+path, {
        method: method,
        //headers: {
        //  "Content-Type": "application/json",
        //},
        body: body,
        // …
      }).then(response => {
        if (!response.ok) {
            return response.json()
                .catch(        () => { throw new Error(response.status); })             // Couldn't parse the JSON
                .then(({message}) => { throw new Error(message || response.status); }); // Got valid JSON with error response, use it
        }
        return response.json();                                                         // Successful response, parse the JSON and return the data
    });
}

async function readFPGATimings() {
    const readButton = document.getElementById("readFPGAButton")
    readButton.innerHTML = "Reading..."
    try {
        data = await httpRequest("/fpga","GET")
        const timingsContainer = document.getElementById("fpgaTimings");
        timingsContainer.innerHTML = ""

        col1 = document.createElement("div")
        col1.style.marginRight = '5px'
        col2 = document.createElement("div")

        Object.entries(data).forEach(([name,val], index) => {
            const timingDiv = createTimingDiv(name,val)
            if (index%2==0) { col1.appendChild(timingDiv) }
            else            { col2.appendChild(timingDiv) }
            console.log(index, val);
        });
        timingsContainer.classList.add("flex-row")
        timingsContainer.appendChild(col1)
        timingsContainer.appendChild(col2)

    } catch (error) {
        readButton.innerHTML = "Read ERROR"
        return
    }
    
    readButton.innerHTML = "Read FPGA"
}

async function writeFPGATimings() {
    const readButton = document.getElementById("writeFPGAButton")
    readButton.innerHTML = "Writing..."
    try {
        data = await httpRequest("/fpga","POST")
    } catch (error) {
        readButton.innerHTML = "Write ERROR"
        return
    }
    
    readButton.innerHTML = "Write FPGA"

    await readFPGATimings()
}

function submitDurations() {
    const form = document.getElementById("durations");
    var data = new FormData(form);

    httpRequest("/durationParam","POST",data)
}

async function readDurations() {
    const form = document.getElementById("durations");
    try {
        data = await httpRequest("/durationParam","GET")
        console.log(data)

        for (par in data) {
            document.getElementById(par).value = data[par]
        }
    } catch (error) {
        return
    }
}

async function readCalcTimings() {
    try {
        data = await httpRequest("/timingParam","GET")
        const timingsContainer = document.getElementById("calcTimings");
        timingsContainer.innerHTML = ""

        col1 = document.createElement("div")
        col1.style.marginRight = '5px'
        col2 = document.createElement("div")

        Object.entries(data).forEach(([name,val], index) => {
            const timingDiv = createTimingDiv(name,val)
            if (index%2==0) { col1.appendChild(timingDiv) }
            else            { col2.appendChild(timingDiv) }
            console.log(index, val);
        });
        timingsContainer.classList.add("flex-row")
        timingsContainer.appendChild(col1)
        timingsContainer.appendChild(col2)

    } catch (error) {
        return
    }
}

async function readServer() {
    const readButton = document.getElementById("readServer")
    readButton.innerHTML = "Reading..."
    try {
        await readDurations()
        await readCalcTimings()
        await getTimingSignalChart()
    } catch (error) {
        readButton.innerHTML = "Read ERROR"
        return
    }
    
    readButton.innerHTML = "Read Server"
}

async function writeServer() {
    const readButton = document.getElementById("writeServer")
    readButton.innerHTML = "Writing..."
    try { submitDurations() }
    catch (error) { readButton.innerHTML = "Write ERROR"; return }
    readButton.innerHTML = "Reading..."
    try { await readCalcTimings() }
    catch (error) { readButton.innerHTML = "Read ERROR";  return }
    readButton.innerHTML = "Send to Server"

    readServer()
}

function createTimingDiv(name,value) {
    const timingDiv   = document.createElement("div"); timingDiv.classList.add("timing-param")
    const timingName  = document.createElement("p"); timingName.innerHTML  = name
    const timingValue = document.createElement("p"); timingValue.innerHTML = value.toFixed(2)
    timingDiv.appendChild(timingName)
    timingDiv.appendChild(timingValue)
    return timingDiv
}

async function getTimingSignalChart() {
    try {
        //data = await httpRequestRaw("/timingChart","GET") // JM: better to use http request, but I'm having trouble requesting image directly from fastapi server
        //console.log("imgData",data)
        //url = URL.createObjectURL(data)
        //console.log("url",url)
        const chartContainer = document.getElementById("timingChart");

        img = document.createElement('img')
        img.setAttribute('src',SERVER_ADDR+"/timingChart?" + new Date().getTime())
        img.setAttribute('height', '300px');
        img.setAttribute('width', '1500px');

        chartContainer.innerHTML = ""
        chartContainer.appendChild(img)
        chartContainer.setAttribute('align-items','center')

    } catch (error) {
        console.log(error)
        return
    }
}

async function saveToFile() {
    await writeServer() // write current settings to server first

    const saveButton = document.getElementById("saveToFile")
    saveButton.innerHTML = "Saving..."
    try { httpRequest("/saveToFile","POST") }
    catch (error) { saveButton.innerHTML = "Save ERROR";  return }
    saveButton.innerHTML = "Save to File"
}

async function readAll() {
    await readServer()
    await readFPGATimings()
}

document.onload =  readAll()



