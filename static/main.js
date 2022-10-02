const submitbuttonElement = document.getElementById("button1");
const renderDivElement = document.getElementById("renderdiv");
const inputBoxElement = document.getElementById("inputbox");
const copyButtonElement = document.getElementById("buttoncopy");
const occasionDivElement = document.getElementById("occasionDiv");

const occasionFinder = function (sentence) {
  let wordsList = [
    "Anniversary",
    "Birthday",
    "Christmas",
    "Easter",
    "Engagement",
    "Father's Day",
    "Halloween",
    "Hanukkah",
    "Hen Party",
    "Mother's Day",
    "New Baby & Christenings",
    "New Year's",
    "Stag Party",
    "Valentine's Day",
    "Wedding",
    "Wedding Gifts",
  ];
  let _return_words = [];
  for (let i = 0; i < wordsList.length; i++) {
    const word = wordsList[i];
    if (sentence.toLowerCase().search(word.toLowerCase()) >= 0) {
      _return_words.push(word);
    } else if (
      sentence.toLowerCase().search("valentine") >= 0 ||
      sentence.toLowerCase().search("valentines") >= 0 ||
      sentence.toLowerCase().search("valentine's") >= 0
    ) {
      _return_words.push("Valentine's Day");
    } else if (
      sentence.toLowerCase().search("fathers day") >= 0 ||
      sentence.toLowerCase().search("father") >= 0 ||
      sentence.toLowerCase().search("father's") >= 0
    ) {
      _return_words.push("Father's Day");
    } else if (
      sentence.toLowerCase().search("mothers day") >= 0 ||
      sentence.toLowerCase().search("mother") >= 0 ||
      sentence.toLowerCase().search("mother's") >= 0
    ) {
      _return_words.push("Mother's Day");
    }
  }
  return _return_words;
};

const addingHtmlInDiv = function () {
  if (window.location.pathname === "/render") {
    occasionDivElement.innerHTML = "";
    renderDivElement.innerHTML = `${inputBoxElement.value}`;
    const array = occasionFinder(renderDivElement.textContent);
    for (let i = 0; i < 4; i++) {
      if (i==1||i==2){
      html = `<input type="text" value="${array[i] ? array[i] : ""}"/>`;
      occasionDivElement.innerHTML += html;}
      else{
        html = `<input type="text" value=""/>`;
        occasionDivElement.innerHTML += html;
      }

    }
  } else {
    const regexp = /(\d+)/g;
    renderDivElement.innerHTML = `[${inputBoxElement.value.match(regexp)}]`;
  }
};

function copyDivToClipboard() {
  var range = document.createRange();
  range.selectNode(renderDivElement);
  window.getSelection().removeAllRanges();
  window.getSelection().addRange(range);
  document.execCommand("copy");
  window.getSelection().removeAllRanges();
}
submitbuttonElement.addEventListener("click", addingHtmlInDiv);
copyButtonElement.addEventListener("click", copyDivToClipboard);


function validateForm() {
  var x = document.forms['form1']["catboxname"].value;
  if (x == "") {
    alert("Category must be filled out");
    return false;
  }
}