
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

        for (let name in data) {
            const timingDiv = createTimingDiv(name,data[name])
            timingsContainer.appendChild(timingDiv)
        }
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

        for (let name in data) {
            const timingDiv = createTimingDiv(name,data[name])
            timingsContainer.appendChild(timingDiv)
        }
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
}

function createTimingDiv(name,value) {
    const timingDiv   = document.createElement("div"); timingDiv.classList.add("timing-param")
    const timingName  = document.createElement("p"); timingName.innerHTML  = name
    const timingValue = document.createElement("p"); timingValue.innerHTML = value.toFixed(2)
    timingDiv.appendChild(timingName)
    timingDiv.appendChild(timingValue)
    return timingDiv
}

async function readAll() {
    await readServer()
    await readFPGATimings()
}

document.onload =  readAll()



