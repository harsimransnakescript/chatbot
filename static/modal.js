document.addEventListener('DOMContentLoaded', () => {

  $(document).ready(function () {
    // When the form is submitted
    $('#submit-modal').click(function (e) {

      e.preventDefault();
      $('.connect-btn').addClass('disabled').css({
        'background': 'transparent',
        'background-color': 'transparent',
        'border-color': 'black',
        'cursor': 'default'
      });
      $('#submit-payment a').addClass('disabled').css({
        'background': 'black',
        'cursor': 'default'
      });
      var response = $('#response').text();
      var name = $('#name').val();
      const email = $('#email').val();


      // Send an AJAX request to the server with the email
      $.ajax({
        url: '/send_emails_user/',
        method: 'POST',
        data: {
          response: response,
          name: name,
          email: email
        },
        success: function (response) {
          // Handle the response from the server here
          // For example, you could show a success message
          // and close the modal
          $('#exampleModal').modal('hide');
        },
        error: function (error) {
          // Handle errors here
          alert('There was an error submitting the form.');
        },

      });
    });
  });





  //Email for agent
  $(document).ready(function () {




      mapboxgl.accessToken = 'pk.eyJ1IjoiaGFyc2ltcmFuMDEiLCJhIjoiY2xoZXFqMDYwMHVoZTNmbWhkMTVxYnJ6YyJ9.LTHSKlce9o52AbIW7W61wA';
      const geocoder = new MapboxGeocoder({
        accessToken: mapboxgl.accessToken,
        types: 'country,region,place,postcode,locality,neighborhood'
      });

      // Get the geocoder results container.
      const results = document.getElementById('result');

      // Add geocoder result to container.
      geocoder.on('result', (e) => {
        // Update the 'result' element with the selected value.
        destination_input = e.result.place_name;
      });

      const radioButtons = document.querySelectorAll('input[name="toggle"]');
let budgetValue = "Medium";  // Set the default value

// Function to handle radio button change
function handleRadioButtonChange() {
  if (this.checked) {
    budgetValue = this.value;
  }
}

// Add event listener to each radio button
radioButtons.forEach(function (radio) {
  radio.addEventListener('change', handleRadioButtonChange);
});

// Set default value if no action has been performed
window.addEventListener('DOMContentLoaded', function () {
  const checkedRadio = document.querySelector('input[name="toggle"]:checked');
  if (!checkedRadio) {
    budgetValue = "Medium";
  }
});


      const labelElement_purpose = document.querySelector('label[for="color_mode_purpose"]');
      labelElement_purpose.addEventListener('click', () => {
        const isChecked = labelElement_purpose.classList.toggle('on');
        Purpose = isChecked ? labelElement_purpose.getAttribute('data-on') : labelElement_purpose.getAttribute('data-off');
      });

      const rangeInput = document.getElementById('myRange');
      let timeoutId;
      rangeInput.addEventListener('input', () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          const currentValue = rangeInput.value;
        }, 500); // delay in milliseconds
      });

      $('#submit-modal').click(function () {
        var destination = localStorage.getItem('destination');
        var Purpose = labelElement_purpose.classList.contains('on') ? labelElement_purpose.getAttribute('data-on') : labelElement_purpose.getAttribute('data-off');
        var response = $('#response').text();
        var name = $('#name').val();
        var email = $('#email').val();
        var contactNumber = $('#number').val();
        duration = rangeInput.value;

        console.log(budgetValue,"value");


        $.ajax({
          type: "POST",
          url: "/send_email_agent/",
          data: {
            destination: destination,
            budget: budgetValue,
            purpose: Purpose,
            duration: duration,
            response: response,
            name: name,
            email: email,
            contact: contactNumber,
          },
          success: function (response) {
            $('#response').html(response);
          },
          error: function (response) {
            alert("Error Ajax");
          },
          complete: function (response) {
            // Clear the modal fields
            $('#name').val('');
            $('#email').val('');
            $('#number').val('');
            // Clear other fields as needed

            $('.connect-btn').removeClass('disabled').removeAttr('style');
            $('#submit-payment a').removeClass('disabled').css({
              'background': '',
              'cursor': ''
            });
            $('#loading1').hide();
          }
        });
      });


  });

});