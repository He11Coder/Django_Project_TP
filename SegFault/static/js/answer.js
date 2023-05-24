function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') 
    {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) 
      {
        const cookie = cookies[i].trim();

        if (cookie.substring(0, name.length + 1) === (name + '=')) 
        {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');


$(".form-check-input").on('click', function(ev){
    const request = new Request(
      'http://127.0.0.1:8000/set_correct/',
      {
          method: 'POST',
          headers: {
              'X-CSRFToken': csrftoken,
              'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
          },
          body: 'answer_id=' + $(this).data('id')
      }
    );
  
    fetch(request).then(
      response_raw => response_raw.json().then(
        response_json => {
          var answer_status = response_json.answer_status;
  
          if (answer_status){
            $(this).prop('checked', true);
          } else {
            $(this).prop('checked', false);
          }
        }
      )
  
    );
  
  });


  $(".ans-btn-true").on('click', function(ev){
    const request = new Request(
      'http://127.0.0.1:8000/vote_answer_up/',
      {
          method: 'POST',
          headers: {
              'X-CSRFToken': csrftoken,
              'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
          },
          body: 'answer_id=' + $(this).data('id')
      }
    );
  
    fetch(request).then(
      response_raw => response_raw.json().then(
        response_json => $('.rating').filter('#' + $(this).data('id')).text("Rating: " + response_json.new_rating)
      ),
      
    );
  
  });
  
  
  $(".ans-btn-false").on('click', function(ev){
    const request = new Request(
      'http://127.0.0.1:8000/vote_answer_down/',
      {
          method: 'POST',
          headers: {
              'X-CSRFToken': csrftoken,
              'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
          },
          body: 'answer_id=' + $(this).data('id')
      }
    );
  
    fetch(request).then(
      response_raw => response_raw.json().then(
        response_json => $('.rating').filter('#' + $(this).data('id')).text("Rating: " + response_json.new_rating)
      )
  
    );
  
  });