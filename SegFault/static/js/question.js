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


$(".btn-success").on('click', function(ev){
  console.log('123');
  const request = new Request(
    'http://127.0.0.1:8000/vote_up/',
    {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        body: 'question_id=' + $(this).data('id')
    }
  );

  fetch(request).then(
    response_raw => response_raw.json().then(
      response_json => $('.rating').filter('#' + $(this).data('id')).text("Rating: " + response_json.new_rating)
    ),
    
  );

});


$(".btn-danger").on('click', function(ev){
  const request = new Request(
    'http://127.0.0.1:8000/vote_down/',
    {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        body: 'question_id=' + $(this).data('id')
    }
  );

  fetch(request).then(
    response_raw => response_raw.json().then(
      response_json => $('.rating').filter('#' + $(this).data('id')).text("Rating: " + response_json.new_rating)
    )

  );

});

