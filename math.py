import scipy.stats as stats





from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)

@app.route('/')
def home():
    return '''

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Normal Distributions</title>
    <style>
        h1 { text-align: center; color: #333; }
        form { width: 50%; display: flex; flex-direction: column; align-items: center; padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9; }
        label, input { margin: 5px 0; }
        button { margin-top: 10px; padding: 5px 10px; background-color: #4CAF50; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #45a049; }
        body { align-items: center; }
        #ansx { text-align: center; }
        #curveContainer { text-align: center; margin-top: 20px; }
        canvas { border: 1px solid #000; }
    </style>
</head>
<body>
    <h1>NORMAL DISTRIBUTIONS</h1>
    <center>
        <h3>Choose the value:</h3>
        <select name="choose" id="choose" onchange="updateForm()">
            <option></option>
            <option id="xval" value="x">x</option>
            <option id="zval" value="z">x</option>
        </select>
    </center>
    <br><br><br>
    <section id="x"></section>
    <section id="z"></section>
    <div id="curveContainer">
        <canvas id="bellCurve" width="600" height="400"></canvas>
    </div>
    <script>
        function updateForm() {
            var selection = document.getElementById("choose").value;
            if (selection == "x") {
                document.getElementById("x").innerHTML = `
                <div><center>
                    <form id="inputFormX" action="/calculate" method="post">
                        <label id="meanLabel">Mean:</label>
                        <input id="mean" name="mean" type="number" step="any">
                        <label id="sdLabel">Standard Deviation:</label>
                        <input id="sd" name="sd" type="number" step="any">
                        <label id="xLabel">x1:</label>
                        <input id="x1" name="x1" type="number" step="any">
                        <label id="xLabel">x2:</label>
                        <input id="x2" name="x2" type="number" step="any">
                        <button type="submit">Calculate Probability</button><br>
                    </form></center>
                    <center><div id="ansx"></div></center>
                </div>
                `;
            }
        }

        // Function to draw the bell curve
        function drawBellCurve(mean, sd) {
            const canvas = document.getElementById("bellCurve");
            const ctx = canvas.getContext("2d");
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const width = canvas.width;
            const height = canvas.height;
            const step = 0.1; // Step for x-axis values

            ctx.beginPath();
            ctx.moveTo(0, height);

            // Calculate points for the bell curve
            for (let x = mean - 4 * sd; x <= mean + 4 * sd; x += step) {
                const y = (1 / (sd * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / sd, 2));
                const xPos = ((x - (mean - 4 * sd)) / (8 * sd)) * width;
                const yPos = height - (y * height * 10); // Scale y for visibility
                ctx.lineTo(xPos, yPos);
            }

            ctx.strokeStyle = "#4CAF50";
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        // Event listener to plot curve when values are input
        document.addEventListener("input", function() {
            const meanInput = document.getElementById("mean");
            const sdInput = document.getElementById("sd");

            if (meanInput && sdInput) {
                const mean = parseFloat(meanInput.value);
                const sd = parseFloat(sdInput.value);

                if (!isNaN(mean) && !isNaN(sd) && sd > 0) {
                    drawBellCurve(mean, sd);
                }
            }
        });
    </script>
</body>
</html>
'''


@app.route('/calculate', methods=['POST'])
def calculate():
    mean = float(request.form['mean'])
    sd = float(request.form['sd'])
    x1 = float(request.form['x1']) if request.form['x1'] else None
    x2 = float(request.form['x2']) if request.form['x2'] else None

    def lookup_z_score(z):
        z = round(z * 100) / 100
        zR = round(z * 10) / 10
        decimal = int(round((abs(z) - abs(zR)) * 100))
        print(z,zR)
        

        nZ = {
            "-3.4": [0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0002],
            "-3.3": [0.0005, 0.0005, 0.0005, 0.0004, 0.0004, 0.0004, 0.0004, 0.0004, 0.0004, 0.0003],
            "-3.2": [0.0007, 0.0007, 0.0006, 0.0006, 0.0006, 0.0006, 0.0006, 0.0005, 0.0005, 0.0005],
            "-3.1": [0.0010, 0.0009, 0.0009, 0.0009, 0.0008, 0.0008, 0.0008, 0.0008, 0.0007, 0.0007],
            "-3.0": [0.0013, 0.0013, 0.0013, 0.0012, 0.0012, 0.0011, 0.0011, 0.0011, 0.0010, 0.0010],
            "-2.9": [0.0019, 0.0018, 0.0018, 0.0017, 0.0016, 0.0016, 0.0015, 0.0015, 0.0014, 0.0014],
            "-2.8": [0.0026, 0.0025, 0.0024, 0.0023, 0.0023, 0.0022, 0.0021, 0.0021, 0.0020, 0.0019],
            "-2.7": [0.0035, 0.0034, 0.0033, 0.0032, 0.0031, 0.0030, 0.0029, 0.0028, 0.0027, 0.0026],
            "-2.6": [0.0047, 0.0045, 0.0044, 0.0043, 0.0041, 0.0040, 0.0039, 0.0038, 0.0037, 0.0036],
            "-2.5": [0.0062, 0.0060, 0.0059, 0.0057, 0.0055, 0.0054, 0.0052, 0.0051, 0.0049, 0.0048],
            "-2.4": [0.0082, 0.0080, 0.0078, 0.0075, 0.0073, 0.0071, 0.0069, 0.0068, 0.0066, 0.0064],
            "-2.3": [0.0107, 0.0104, 0.0102, 0.0099, 0.0096, 0.0094, 0.0091, 0.0089, 0.0087, 0.0084],
            "-2.2": [0.0139, 0.0136, 0.0132, 0.0129, 0.0125, 0.0122, 0.0119, 0.0116, 0.0113, 0.0110],
            "-2.1": [0.0179, 0.0174, 0.0170, 0.0166, 0.0162, 0.0158, 0.0154, 0.0150, 0.0146, 0.0143],
            "-2.0": [0.0228, 0.0222, 0.0217, 0.0212, 0.0207, 0.0202, 0.0197, 0.0192, 0.0188, 0.0183],
            "-1.9": [0.0287, 0.0281, 0.0274, 0.0268, 0.0262, 0.0256, 0.0250, 0.0244, 0.0239, 0.0233],
            "-1.8": [0.0359, 0.0351, 0.0344, 0.0336, 0.0329, 0.0322, 0.0314, 0.0307, 0.0301, 0.0294],
            "-1.7": [0.0446, 0.0436, 0.0427, 0.0418, 0.0409, 0.0401, 0.0392, 0.0384, 0.0375, 0.0367],
            "-1.6": [0.0548, 0.0537, 0.0526, 0.0516, 0.0505, 0.0495, 0.0485, 0.0475, 0.0465, 0.0455],
            "-1.5": [0.0668, 0.0655, 0.0643, 0.0630, 0.0618, 0.0606, 0.0594, 0.0582, 0.0571, 0.0559],
            "-1.4": [0.0808, 0.0793, 0.0778, 0.0764, 0.0749, 0.0735, 0.0721, 0.0708, 0.0694, 0.0681],
            "-1.3": [0.0968, 0.0951, 0.0934, 0.0918, 0.0901, 0.0885, 0.0869, 0.0853, 0.0838, 0.0823],
            "-1.2": [0.1151, 0.1131, 0.1112, 0.1093, 0.1075, 0.1056, 0.1038, 0.1020, 0.1003, 0.0985],
            "-1.1": [0.1357, 0.1335, 0.1314, 0.1292, 0.1271, 0.1251, 0.1230, 0.1210, 0.1190, 0.1170],
            "-1.0": [0.1587, 0.1562, 0.1539, 0.1515, 0.1492, 0.1469, 0.1446, 0.1423, 0.1401, 0.1379],
            "-0.9": [0.1841, 0.1814, 0.1788, 0.1762, 0.1736, 0.1711, 0.1685, 0.1660, 0.1635, 0.1611],
            "-0.8": [0.2119, 0.2090, 0.2061, 0.2033, 0.2005, 0.1977, 0.1949, 0.1922, 0.1894, 0.1867],
            "-0.7": [0.2420, 0.2389, 0.2358, 0.2327, 0.2296, 0.2266, 0.2236, 0.2206, 0.2177, 0.2148],
            "-0.6": [0.2743, 0.2709, 0.2676, 0.2643, 0.2611, 0.2578, 0.2546, 0.2514, 0.2483, 0.2451],
            "-0.5": [0.3085, 0.3050, 0.3015, 0.2981, 0.2946, 0.2912, 0.2877, 0.2843, 0.2810, 0.2776],
            "-0.4": [0.3446, 0.3409, 0.3372, 0.3336, 0.3300, 0.3263, 0.3226, 0.3190, 0.3153, 0.3117],
            "-0.3": [0.3821, 0.3784, 0.3747, 0.3710, 0.3672, 0.3635, 0.3598, 0.3560, 0.3523, 0.3485],
            "-0.2": [0.4207, 0.4170, 0.4131, 0.4092, 0.4052, 0.4013, 0.3974, 0.3934, 0.3895, 0.3855],
            "-0.1": [0.4602, 0.4562, 0.4522, 0.4482, 0.4441, 0.4401, 0.4360, 0.4320, 0.4279, 0.4238],
            "-0.0": [0.5000, 0.4960, 0.4920, 0.4880, 0.4840, 0.4800, 0.4760, 0.4720, 0.4680, 0.4640],
            };


        zP = {
            "0.0": [0.5000, 0.4960, 0.4920, 0.4880, 0.4840, 0.4801, 0.4761, 0.4721, 0.4681, 0.4641],
            "0.1": [0.4602, 0.4562, 0.4522, 0.4483, 0.4443, 0.4404, 0.4364, 0.4325, 0.4286, 0.4247],
            "0.2": [0.4207, 0.4168, 0.4129, 0.4090, 0.4052, 0.4013, 0.3974, 0.3936, 0.3897, 0.3859],
            "0.3": [0.3821, 0.3783, 0.3745, 0.3707, 0.3669, 0.3632, 0.3594, 0.3557, 0.3520, 0.3483],
            "0.4": [0.3446, 0.3409, 0.3372, 0.3336, 0.3300, 0.3264, 0.3228, 0.3192, 0.3156, 0.3121],
            "0.5": [0.3085, 0.3050, 0.3015, 0.2981, 0.2946, 0.2912, 0.2877, 0.2843, 0.2810, 0.2776],
            "0.6": [0.2743, 0.2709, 0.2676, 0.2643, 0.2611, 0.2578, 0.2546, 0.2514, 0.2483, 0.2451],
            "0.7": [0.2420, 0.2389, 0.2358, 0.2327, 0.2296, 0.2266, 0.2236, 0.2206, 0.2177, 0.2148],
            "0.8": [0.2119, 0.2090, 0.2061, 0.2033, 0.2005, 0.1977, 0.1949, 0.1922, 0.1894, 0.1867],
            "0.9": [0.1841, 0.1814, 0.1788, 0.1762, 0.1736, 0.1711, 0.1685, 0.1660, 0.1635, 0.1611],
            "1.0": [0.1587, 0.1562, 0.1539, 0.1515, 0.1492, 0.1469, 0.1446, 0.1423, 0.1401, 0.1379],
            "1.1": [0.1357, 0.1335, 0.1314, 0.1292, 0.1271, 0.1251, 0.1230, 0.1210, 0.1190, 0.1170],
            "1.2": [0.1151, 0.1131, 0.1112, 0.1093, 0.1075, 0.1056, 0.1038, 0.1020, 0.1003, 0.0985],
            "1.3": [0.0968, 0.0951, 0.0934, 0.0918, 0.0901, 0.0885, 0.0869, 0.0853, 0.0838, 0.0823],
            "1.4": [0.0808, 0.0793, 0.0778, 0.0764, 0.0749, 0.0735, 0.0721, 0.0708, 0.0694, 0.0681],
            "1.5": [0.0668, 0.0655, 0.0643, 0.0630, 0.0618, 0.0606, 0.0594, 0.0582, 0.0571, 0.0559],
            "1.6": [0.0548, 0.0537, 0.0526, 0.0516, 0.0505, 0.0495, 0.0485, 0.0475, 0.0465, 0.0455],
            "1.7": [0.0446, 0.0436, 0.0427, 0.0418, 0.0409, 0.0401, 0.0392, 0.0384, 0.0375, 0.0367],
            "1.8": [0.0359, 0.0351, 0.0344, 0.0336, 0.0329, 0.0322, 0.0314, 0.0307, 0.0301, 0.0294],
            "1.9": [0.0287, 0.0281, 0.0274, 0.0268, 0.0262, 0.0256, 0.0250, 0.0244, 0.0239, 0.0233],
            "2.0": [0.0228, 0.0222, 0.0217, 0.0212, 0.0207, 0.0202, 0.0197, 0.0192, 0.0188, 0.0183],
            "2.1": [0.0179, 0.0174, 0.0170, 0.0166, 0.0162, 0.0158, 0.0154, 0.0150, 0.0146, 0.0143],
            "2.2": [0.0139, 0.0136, 0.0132, 0.0129, 0.0125, 0.0122, 0.0119, 0.0116, 0.0113, 0.0110],
            "2.3": [0.0107, 0.0104, 0.0102, 0.0099, 0.0096, 0.0094, 0.0091, 0.0089, 0.0087, 0.0084],
            "2.4": [0.0082, 0.0080, 0.0078, 0.0075, 0.0073, 0.0071, 0.0069, 0.0068, 0.0066, 0.0064],
            "2.5": [0.0062, 0.0060, 0.0059, 0.0057, 0.0055, 0.0054, 0.0052, 0.0051, 0.0049, 0.0048],
            "2.6": [0.0047, 0.0045, 0.0044, 0.0043, 0.0041, 0.0040, 0.0039, 0.0038, 0.0037, 0.0036],
            "2.7": [0.0035, 0.0034, 0.0033, 0.0032, 0.0031, 0.0030, 0.0029, 0.0028, 0.0027, 0.0026],
            "2.8": [0.0026, 0.0025, 0.0024, 0.0023, 0.0023, 0.0022, 0.0021, 0.0021, 0.0020, 0.0019],
            "2.9": [0.0019, 0.0018, 0.0018, 0.0017, 0.0016, 0.0016, 0.0015, 0.0015, 0.0014, 0.0014],
            "3.0": [0.0013, 0.0013, 0.0012, 0.0012, 0.0011, 0.0011, 0.0011, 0.0010, 0.0010, 0.0009],
            "3.1": [0.0009, 0.0008, 0.0008, 0.0008, 0.0007, 0.0007, 0.0007, 0.0007, 0.0006, 0.0006],
            "3.2": [0.0006, 0.0005, 0.0005, 0.0005, 0.0004, 0.0004, 0.0004, 0.0004, 0.0004, 0.0003],
            "3.3": [0.0004, 0.0004, 0.0004, 0.0004, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003],
            "3.4": [0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0003, 0.0002, 0.0002],
            };
        if z < 0:
            return nZ[str(zR)][decimal]
        else:
            return zP[str(zR)][decimal]


    result = None
    if x1 and x2:
        z1 = (x1 - mean) / sd
        z2 = (x2 - mean) / sd
        p1 = lookup_z_score(z1)
        p2 = lookup_z_score(z2)
        result = p2 - p1
    elif x1:
        z1 = (x1 - mean) / sd
        result = 1 - lookup_z_score(z1)
    elif x2:
        z2 = (x2 - mean) / sd
        result = lookup_z_score(z2)

    x = np.linspace(mean - 4 * sd, mean + 4 * sd, 1000)
    y = stats.norm.pdf(x, mean, sd)

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, color='green')
    plt.title('Bell Curve')
    plt.xlabel('X values')
    plt.ylabel('Probability Density Function')
    

    if x1 is not None and x2 is not None:
        plt.fill_between(x, y, where=(x >= x1) & (x <= x2), color='lightgreen', alpha=0.5)
    elif x1 is not None:
        plt.fill_between(x, y, where=(x >= x1), color='lightgreen', alpha=0.5)
    elif x2 is not None:
        plt.fill_between(x, y, where=(x <= x2), color='lightgreen', alpha=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    
    return f'''
    <certer><h1>Calculated Probability</h1>
    <h3>Result: {result}</h3>
    <img src="data:image/png;base64,{image_base64}" alt="Bell Curve"/>
    <div id="ansx">Probability calculations go here...</div>
    <a href="/">Go back</a></center>
    '''

if __name__ == '__main__':
    app.run(debug=True)


