let setGraph = (res, chart, fromDate, toDate) => {
  let diffMin = Math.floor((toDate-fromDate)/ 60000); // 320
  let bucketamt = 20;
  let twitterData = new Array(diffMin/bucketamt).fill(0);

  if(res['error']){
      throw new Error(res['error']['message']);
  } else {
      for(i=0; i<res['results'].length; i++){
          let time = res['results'][i]['created_at']; // i.e. 'Mon Jun 17 18:11:13 +0000 2019'
          let timedate = new Date(time);
          let diffStartMin = Math.floor((timedate - fromDate) / 60000);
          let bucket = Math.floor(diffStartMin/bucketamt);
          twitterData[bucket] += 1;
      }
      let labels = [];

      for(i=0; i<diffMin/bucketamt; i++) {
          let s = String(i*bucketamt + '-' + (i+1)*bucketamt + ' min')
          labels.push(s);
      }

      let barChartData = {
          label: 'Twitter Data',
          data: twitterData,
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgb(54, 162, 235)',
          fill: false
      };

      chart.config.data.datasets.push(barChartData);
      chart.config.data.labels = labels;
      chart.update();
  }
} // set the graph given a json response

let getToken = async function(authkey) {
  let proxy = 'https://cors-anywhere.herokuapp.com/';
  let tokenUrl = proxy + 'https://api.twitter.com/oauth2/token';

  let tokenParams = {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
      'Authorization': 'Basic ' + authkey,
    },
    body: 'grant_type=client_credentials',
    method: 'POST'
  };

  let data;
  try {
    data = await fetch(tokenUrl, tokenParams) // return this promise
  }
  catch (error) {
    const data = undefined;
  }
  const res = data.json();
  if (res['access_token']) {
    window.localStorage.setItem('access_token', res['access_token']);
  }
}

let getSinglePage = async function(next='none', options) {
  let proxy = 'https://cors-anywhere.herokuapp.com/';
  let query = String('point_radius:['+ options['lon'] + ' ' + options['lat'] + ' ' + '1mi'+']');
  let urlEncodedQuery = encodeURIComponent(query);
  let access_token = window.localStorage.getItem('access_token');
  let access_token_str = 'Bearer ' + access_token;
  let twitter_env_name = 'vidCaptureDevEnv'; //the name of the twitter environment, can pass in as parameter

  let get_url = proxy+'https://api.twitter.com/1.1/tweets/search/fullarchive/'+ twitter_env_name +'.json?query='
  + urlEncodedQuery
  + '&maxResults=100'
  + '&fromDate='
  + options['fromDate']
  + '&toDate='
  + options['toDate'];

  let params = {
    headers: {
    'Authorization': access_token_str
    },
    method: 'GET'
  }

  if(next != 'none'){
    get_url += '&next='+next;
  }

  let singlePage = await fetch(get_url, params)
  .then(resp => {
    return resp.json();
  });

  return singlePage;
}

let getAllPages = async function(next='none', options){
  let single_results = await getSinglePage(next, options);
  if(single_results.next) {
    return single_results.results.concat(await(getAllPages(single_results.next, options))); // return an array with only the results
  } else {
    return single_results.results;
  }
};

let fetchAll = async function(authkey, options, chart){

  await getToken(authkey);

  const entireList = await getAllPages('none', options);

  let fd = options['fromDate'];
  let td = options['toDate'];
  let fromDate = new Date(fd.substring(0,4)
    +'-'+fd.substring(4,6)+'-'+fd.substring(6,8)+'T'
    +fd.substring(8,10)+':'+fd.substring(10, 12) + ':00Z');

  let toDate = new Date(td.substring(0,4)
    +'-'+td.substring(4,6)+'-'+td.substring(6,8)+'T'
    +td.substring(8,10)+':'+td.substring(10, 12) + ':00Z');

  setGraph({'results': entireList}, chart, fromDate, toDate);
}
