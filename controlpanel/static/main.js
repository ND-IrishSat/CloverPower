// Auto-update data every second
function fetchData() {
  fetch('/data')
    .then(response => response.json())
    .then(data => {
      // Update PAC1934 (0x10)
      const pac10 = data.pac1934_0x10;
      let html = `<tr><td colspan="5">Address: ${pac10.address}</td></tr>`;
      pac10.channels.forEach((ch, index) => {
        html += `<tr>
          <td>${index + 1}</td>
          <td>${ch.label}</td>
          <td>${ch.voltage}</td>
          <td>${ch.current}</td>
          <td>${ch.power}</td>
        </tr>`;
      });
      document.querySelector("#pac1934_0x10 .device-data").innerHTML = html;

      // Update PAC1934 (0x17)
      const pac17 = data.pac1934_0x17;
      html = `<tr><td colspan="5">Address: ${pac17.address}</td></tr>`;
      pac17.channels.forEach((ch, index) => {
        html += `<tr>
          <td>${index + 1}</td>
          <td>${ch.label}</td>
          <td>${ch.voltage}</td>
          <td>${ch.current}</td>
          <td>${ch.power}</td>
        </tr>`;
      });
      document.querySelector("#pac1934_0x17 .device-data").innerHTML = html;

      // Update BQ25672 registers
      const bq = data.bq25672;
      html = `<tr><td colspan="5">Address: ${bq.address}</td></tr>`;
      bq.registers.forEach(reg => {
        html += `<tr>
          <td>${reg.reg}</td>
          <td>${reg.name}</td>
          <td>${reg.binary}</td>
          <td>${reg.value}</td>
          <td>${reg.unit}</td>
        </tr>`;
      });
      document.querySelector("#bq25672 .device-data").innerHTML = html;
      
      // Update extra BQ25672 info
      document.getElementById("mppt-status").innerText = bq.extra.mppt;
      document.getElementById("ico-status").innerText = bq.extra.ico;
      document.getElementById("charge-status").innerText = bq.extra.charge_status;

      // Update PCA9557
      const pca = data.pca9557;
      html = "";
      const pinLabels = {
        0: "Flight Computer",
        1: "Payload",
        2: "Heat",
        3: "Motor",
        4: "SDR"
      };
      for (let pin = 0; pin < 5; pin++) {
        const status = pca.pins.find(p => p.pin === pinLabels[pin])?.status || "Unknown";
        html += `<tr>
          <td>${pinLabels[pin]}</td>
          <td>${status}</td>
          <td>
            <button class="pca9557-high" data-pin="${pin}">High</button>
            <button class="pca9557-low" data-pin="${pin}">Low</button>
            <button class="pca9557-hiz" data-pin="${pin}">HIZ</button>
          </td>
        </tr>`;
      }
      document.querySelector("#pca9557 .device-data").innerHTML = html;

      // Add event listeners for PCA9557 control buttons
      document.querySelectorAll(".pca9557-high").forEach(button => {
        button.addEventListener("click", function() {
          const pin = this.getAttribute("data-pin");
          const formData = new FormData();
          formData.append("pin", pin);
          fetch("/pca9557_set_high", {
            method: "POST",
            body: formData
          })
          .then(response => response.json())
          .then(data => console.log(data.message))
          .catch(error => console.error(error));
        });
      });

      document.querySelectorAll(".pca9557-low").forEach(button => {
        button.addEventListener("click", function() {
          const pin = this.getAttribute("data-pin");
          const formData = new FormData();
          formData.append("pin", pin);
          fetch("/pca9557_set_low", {
            method: "POST",
            body: formData
          })
          .then(response => response.json())
          .then(data => console.log(data.message))
          .catch(error => console.error(error));
        });
      });

      document.querySelectorAll(".pca9557-hiz").forEach(button => {
        button.addEventListener("click", function() {
          const pin = this.getAttribute("data-pin");
          const formData = new FormData();
          formData.append("pin", pin);
          fetch("/pca9557_set_hiz", {
            method: "POST",
            body: formData
          })
          .then(response => response.json())
          .then(data => console.log(data.message))
          .catch(error => console.error(error));
        });
      });
    })
    .catch(error => console.error("Error fetching data:", error));
}

setInterval(fetchData, 1000);
fetchData();

// Handle custom read form submission
document.getElementById("custom-read-form").addEventListener("submit", function(e) {
  e.preventDefault();
  const formData = new FormData(e.target);
  fetch("/custom_read", {
    method: "POST",
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    let result = "";
    if(data.status === "success") {
      result = `Value: ${data.value} (binary)`;
    } else {
      result = `Error: ${data.message}`;
    }
    document.getElementById("read-result").innerText = result;
  });
});

// Handle custom write form submission
document.getElementById("custom-write-form").addEventListener("submit", function(e) {
  e.preventDefault();
  const formData = new FormData(e.target);
  fetch("/custom_write", {
    method: "POST",
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    let result = "";
    if(data.status === "success") {
      result = data.message;
    } else {
      result = `Error: ${data.message}`;
    }
    document.getElementById("write-result").innerText = result;
  });
});

// Handle MPPT and ICO button clicks (remove alerts)
document.getElementById("enable-mppt").addEventListener("click", function() {
  fetch("/mppt_enable", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});
document.getElementById("disable-mppt").addEventListener("click", function() {
  fetch("/mppt_disable", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});
document.getElementById("enable-ico").addEventListener("click", function() {
  fetch("/ico_enable", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});
document.getElementById("disable-ico").addEventListener("click", function() {
  fetch("/ico_disable", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});

// Handle ADC button clicks (remove alerts)
document.getElementById("adc-enable").addEventListener("click", function() {
  fetch("/adc_enable", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});
document.getElementById("adc-disable").addEventListener("click", function() {
  fetch("/adc_disable", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});

// Handle Reset button click
document.getElementById("bq25672-reset").addEventListener("click", function() {
  fetch("/bq25672_reset", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});

// Handle Watchdog Disable button click
document.getElementById("bq25672-watchdog-disable").addEventListener("click", function() {
  fetch("/bq25672_watchdog_disable", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});

// Handle HVDCP button clicks
document.getElementById("enable-hvdcp").addEventListener("click", function() {
  fetch("/enable_hvdcp", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});

document.getElementById("disable-hvdcp").addEventListener("click", function() {
  fetch("/disable_hvdcp", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});

document.getElementById("set-9v").addEventListener("click", function() {
  fetch("/set_9v", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});

document.getElementById("set-12v").addEventListener("click", function() {
  fetch("/set_12v", { method: "POST" })
    .then(response => response.json())
    .then(data => console.log(data.message))  // Log instead of alert
    .catch(error => console.error(error));
});