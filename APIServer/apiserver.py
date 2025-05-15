from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from timingController import timingController
from pythonlib.timinglib import TimingParam, DurationParam

app = FastAPI()

# Enable CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

controller = timingController()

@app.get("/")
def read_root():
    return "MRTOF Timing System Control"

@app.get("/fpga")
def read_from_FPGA():
    controller.updateFPGATimings()
    data = controller.readFPGATimings()
    fpga_dict = {}
    for i in range(len(data)): fpga_dict[TimingParam(i).name] = data[i]
    return fpga_dict

@app.post("/fpga")
def write_to_FPGA():
    controller.writeOneShotArrayInFPGAviaTCP()
    controller.executeTimingsInFPGAviaTCP()
    return

@app.get("/timingParam")
def read_TimingParams():
    data = controller.readTimings()
    timing_dict = {}
    for i in range(len(data)): timing_dict[TimingParam(i).name] = data[i]
    return timing_dict

@app.get("/durationParam")
def read_DurationParams():
    data = controller.readDurations()
    duration_dict = {}
    for i in range(len(data)): duration_dict[DurationParam(i).name] = data[i]
    return duration_dict

@app.post("/durationParam")
async def update_DurationParams(request: Request):
    form_data = await request.form()
    data_dict = {}
    for i in form_data: data_dict[i] = form_data[i]
    controller.updateDurationParameters(data_dict)