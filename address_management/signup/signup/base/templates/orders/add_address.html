{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{% if address %}Edit Address{% else %}Add Address{% endif %}</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<style>
body { font-family: Arial, sans-serif; background:#f5f5f5; padding:20px; }
.container { max-width:800px; margin:auto; background:#fff; padding:25px; border-radius:10px; box-shadow:0 5px 15px rgba(0,0,0,0.1); }
h2 { text-align:center; margin-bottom:20px; color:#000; }
label { display:block; margin-bottom:5px; font-weight:600; }
.required { color:red; }
.row { display:flex; gap:20px; flex-wrap:wrap; }
.col { flex:1; min-width:48%; }

input, select { width:100%; padding:10px; margin-bottom:15px; border-radius:6px; border:1px solid #ccc; font-size:1rem; }
.phone-input { display:flex; gap:5px; }
.phone-input select { width:35%; }
.phone-input input { width:65%; }

button, .location-btn { width:100%; padding:12px; border:none; border-radius:6px; background:#000; color:#fff; font-size:1rem; cursor:pointer; margin-bottom:10px; }
button:hover, .location-btn:hover { background:#333; }

.back-link { display:block; margin-top:15px; text-align:center; }

/* Mobile Responsive */
@media(max-width:600px){
  .row { flex-direction:column; }
  .col { min-width:100%; }
}
</style>
</head>
<body>

<div class="container">
<h2>{% if address %}Edit Address{% else %}Add Address{% endif %}</h2>

{% if messages %}
  {% for message in messages %}
    <p style="color:green">{{ message }}</p>
  {% endfor %}
{% endif %}

<form method="POST">
{% csrf_token %}

<!-- Full Width -->
<label>Full Name <span class="required">*</span></label>
<input type="text" name="fullname" value="{{ address.fullname|default:'' }}" required>

<!-- Row 1 -->
<div class="row">
  <div class="col">
    <label>Mobile Number <span class="required">*</span></label>
    <div class="phone-input">
      <select name="country_code" required>
        <option value="+91" selected>🇮🇳 +91</option>
        <option value="+1">🇺🇸 +1</option>
        <option value="+44">🇬🇧 +44</option>
        <option value="+61">🇦🇺 +61</option>
      </select>
      <input type="tel" name="mobile" value="{{ address.mobile|default:'' }}" required>
    </div>
  </div>
  <div class="col">
    <label>PIN Code <span class="required">*</span></label>
    <input type="text" id="pincode" name="pincode" maxlength="6" value="{{ address.pincode|default:'' }}" required>
  </div>
</div>

<!-- Row 2 -->
<div class="row">
  <div class="col">
    <label>Address Line 1 <span class="required">*</span></label>
    <input type="text" id="address1" name="address1" placeholder="House No, Street, Area" value="{{ address.address1|default:'' }}" required>
  </div>
  <div class="col">
    <label>Address Line 2 <span class="required">*</span></label>
    <input type="text" id="address2" name="address2"placeholder="Colony, Locality, Landmark " value="{{ address.address2|default:'' }}" required>
  </div>
</div>

<!-- Row 3 -->
<div class="row">
  <div class="col">
    <label>City <span class="required">*</span></label>
    <input type="text" id="city" name="city"placeholder="Auto-filled or enter manually" value="{{ address.city|default:'' }}" required>
  </div>
  <div class="col">
    <label>State <span class="required">*</span></label>
    <input type="text" id="state" name="state"placeholder="Auto-filled or enter manually" value="{{ address.state|default:'' }}" required>
  </div>
</div>

<!-- Row 4 -->
<div class="row">
  <div class="col">
    <label>Country <span class="required">*</span></label>
    <select id="country" name="country" required>
      <option value="India" selected>India</option>
      <option value="United States">United States</option>
      <option value="United Kingdom">United Kingdom</option>
      <option value="Australia">Australia</option>
      <option value="United Arab Emirates">United Arab Emirates</option>
    </select>
  </div>
  <div class="col">
    <label>Landmark</label>
    <input type="text" id="landmark" name="landmark" placeholder="near by landmamrk"value="{{ address.landmark|default:'' }}">
  </div>
</div>

<!-- Location Button & Submit -->
<button type="button" class="location-btn" onclick="getLocation()"><i class="fa-solid fa-location-dot"></i> Use My Current Location</button>
<p id="location-status"></p>

<button type="submit">{% if address %}Update Address{% else %}Save Address{% endif %}</button>

</form>

<a href="{% url 'base:address_list' %}" class="back-link">Back to Address List</a>
</div>


<script>
// Auto-fill City/State using Pincode (India)
document.getElementById("pincode").addEventListener("input", async function() {
  const pin = this.value;
  if(pin.length === 6){
    const res = await fetch(`https://api.postalpincode.in/pincode/${pin}`);
    const data = await res.json();
    if(data[0].Status === "Success"){
      document.getElementById("city").value = data[0].PostOffice[0].District;
      document.getElementById("state").value = data[0].PostOffice[0].State;
    }
  }
});

// Fetch Location & Autofill
async function getLocation(){
  const status = document.getElementById("location-status");
  if(navigator.geolocation){
    navigator.geolocation.getCurrentPosition(async (pos)=>{
      const {latitude: lat, longitude: lon} = pos.coords;
      status.textContent = "Fetching location...";
      const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}`);
      const data = await res.json();
      document.getElementById("address1").value = data.address.house_number || data.address.road || "";
      document.getElementById("address2").value = data.address.suburb || data.address.neighbourhood || "";
      document.getElementById("city").value = data.address.city || data.address.town || "";
      document.getElementById("state").value = data.address.state || "";
      document.getElementById("pincode").value = data.address.postcode || "";
      status.textContent = "Location filled!";
    });
  } else {
    status.textContent = "Geolocation not supported.";
  }
}
</script>

</body>
</html>
