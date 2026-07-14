/**
* Edits the number prototype to allow money formatting
*
* @param fixed the number to fix the decimal at. Default 2.
* @param decimalDelim the string to deliminate the non-decimal
*        parts of the number and the decimal parts with. Default "."
* @param breakdDelim the string to deliminate the non-decimal
*        parts of the number with. Default ","
* @return returns this number as a USD-money-formatted String
*		  like this: x,xxx.xx
*/
Number.prototype.money = function(fixed, decimalDelim, breakDelim){
	var n = this, 
	fixed = isNaN(fixed = Math.abs(fixed)) ? 2 : fixed, 
	decimalDelim = decimalDelim == undefined ? "." : decimalDelim, 
	breakDelim = breakDelim == undefined ? "," : breakDelim, 
	negative = n < 0 ? "-" : "", 
	i = parseInt(n = Math.abs(+n || 0).toFixed(fixed)) + "", 
	j = (j = i.length) > 3 ? j % 3 : 0;
	return negative + (j ? i.substr(0, j) +
		 breakDelim : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + breakDelim) +
		  (fixed ? decimalDelim + Math.abs(n - i).toFixed(fixed).slice(2) : "");
}

/**
* Plays a sound via HTML5 through Audio tags on the page
*
* @require the id must be the id of an <audio> tag.
* @param id the id of the element to play
* @param loop the boolean flag to loop or not loop this sound
*/
startSound = function(id, loop) {
    
	soundHandle = document.getElementById(id);
	if(loop)
		soundHandle.setAttribute('loop', loop);
	
    if(soundHandle == null)
        console.log("Error with Sound : SoundHandler is null")
    else {
        soundHandle.play();
        console.log("Sound works")
    }
     
    
}

/**
* The View Model that represents one game of
* Who Wants to Be a Millionaire.
* 
* @param data the question bank to use
*/
var MillionaireModel = function(data) {
	var self = this;
    var help = -1

    // Question memory bank
    this.history = [];

	// The 15 questions of this game
    this.questions = data.questions;

    // A flag to keep multiple selections
    // out while transitioning levels
    this.transitioning = false;

    // The current money obtained
 	this.money = new ko.observable(0);

 	// The current level(starting at 1) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<STARTING LEVEL
    this.level = new ko.observable(
        Number(sessionStorage.getItem("currentLevel")) || 12
    );

 	// The three the user can use to 
 	// attempt to answer a question (1 use each)
 	this.usedFifty = new ko.observable(false);
 	this.usedPhone = new ko.observable(false);
 	this.usedAudience = new ko.observable(false);

    var gameMode = localStorage.getItem("gameMode") || "game";
    console.log("Game mode:", gameMode);

 	// Grabs the question text of the current question
 	self.getQuestionText = function() {
 		return self.questions[self.level() - 1].question;
 	}

 	// Gets the answer text of a specified question index (0-3)
 	// from the current question
 	self.getAnswerText = function(index) {
 		return self.questions[self.level() - 1].content[index];
 	}

 	// Uses the fifty-fifty option of the user
 	self.fifty = function(item, event) {
 		if(self.transitioning)
 			return;
 		$(event.target).fadeOut('slow');
 		var correct = this.questions[self.level() - 1].correct;
 		var first = (correct + 1) % 4;
 		var second = (first + 1) % 4;
 		if(first == 0 || second == 0) {
 			$("#answer-one").fadeOut('slow');
 		}
 		if(first == 1 || second == 1) {
 			$("#answer-two").fadeOut('slow');
 		}
 		if(first == 2 || second == 2) {
 			$("#answer-three").fadeOut('slow');
 		}
 		if(first == 3 || second == 3) {
 			$("#answer-four").fadeOut('slow');
 		}
 	}
    
    
    
    //Uses the phone a friend option
    self.friend = function(item, event) {
        if(self.transitioning)
            return;
        $(event.target).fadeOut('slow');
        $("#phoneImage").fadeIn('slow');
        var correct = this.questions[self.level() - 1].correct;
        
        //Random to decide whether to use 95% or 50/50
        rand = Math.random()
        console.log("2 Options random = " + rand)
        var elm = this.questions[self.level() - 1].correct
        console.log("elm = " + elm)
        
        //80% correct option
        if(rand <= .50) {
            rand = Math.random()
            console.log("80% Random = " + rand)
            var elm = this.questions[self.level() - 1].correct
            console.log("elm = " + elm)
            
            var chosenNum = -1
            if(rand <= .80) {
                chosenNum = elm
            }
            else {
                chosenNum = getRandomInt(0, 3)
                console.log("Wrong Element:" + chosenNum)
            }
            
            var correctLetter = "";
            if(chosenNum == 0) {
               correctLetter = "A";
            }
            if(chosenNum == 1) {
                correctLetter = "B";
            }
            if(chosenNum == 2 ) {
                correctLetter = "C";
            }
            if(chosenNum== 3) {
                correctLetter = "D";
            }
            help = 1
            textToDisplay = "Your friend thinks the correct answer is " + correctLetter;
            $("#display-help").fadeIn('slow');
            document.getElementById("display-help").innerHTML = textToDisplay;
        }
        //50/50 option from friend
        else {
            var correct = this.questions[self.level() - 1].correct;
            var first = (correct + 1) % 4;
            var second = (first + 1) % 4;
            if(first == 0 || second == 0) {
                $("#answer-one").fadeOut('slow');
            }
            if(first == 1 || second == 1) {
                $("#answer-two").fadeOut('slow');
            }
            if(first == 2 || second == 2) {
                $("#answer-three").fadeOut('slow');
            }
            if(first == 3 || second == 3) {
                $("#answer-four").fadeOut('slow');
            }
            help = 1
            textToDisplay = "Your friend thinks one of these is the correct answer.";
            $("#display-help").fadeIn('slow');
            document.getElementById("display-help").innerHTML = textToDisplay;

        }
        
    }
    
    function getRandomInt(min, max) {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function getGameMode() {
        return localStorage.getItem("gameMode") || "game";
    }
 
    //Uses the audience option
    self.audience = function(item, event) {
        if(self.transitioning)
            return;
        $(event.target).fadeOut('slow');
        
        
        rand = Math.random()
        console.log("Random = " + rand)
        var elm = this.questions[self.level() - 1].correct
        console.log("elm = " + elm)
        
        var chosenNum = -1
        if(rand <= .75) {
            chosenNum = elm
        }
        else {
            chosenNum = getRandomInt(0, 3)
            console.log("Wrong Element:" + chosenNum)
        }
        
        var correctLetter = "";
        if(chosenNum == 0) {
           correctLetter = "A";
        }
        if(chosenNum == 1) {
            correctLetter = "B";
        }
        if(chosenNum == 2 ) {
            correctLetter = "C";
        }
        if(chosenNum== 3) {
            correctLetter = "D";
        }
        
        help = 1
        console.log("CorrectLetter: " + correctLetter)
        textToDisplay = "The audience thinks the correct answer is " + correctLetter;
        $("#display-help").fadeIn('slow');
        document.getElementById("display-help").innerHTML = textToDisplay;
        
    }

 	// Fades out an option used if possible
 	self.fadeOutOption = function(item, event) {
 		if(self.transitioning)
 			return;
 		$(event.target).fadeOut('slow');
 	}


 	// Attempts to answer the question with the specified
 	// answer index (0-3) from a click event of elm
 	self.answerQuestion = function(index, elm) {
 		if(self.transitioning)
 			return;
 		self.transitioning = true;
        if(help == 1){
            $("#phoneImage").fadeOut('slow');
            $("#display-help").fadeOut('slow');
            //document.getElementById("display-help").innerHTML = "";
            help = -1
        }

        var isCorrect = self.questions[self.level() - 1].correct == index;
        
        //Log the user's choice 
        self.logAnswer(index, isCorrect);
        
 		if(isCorrect) {
 			self.rightAnswer(elm);
 		} else {
 			self.wrongAnswer(elm);
 		}
 	}

    self.logAnswer = function(index, isCorrect) {
        var q = self.questions[self.level() - 1];

        self.history.push({
            question: q.question,
            selected: q.content[index],
            correct: q.content[q.correct],
            isCorrect: isCorrect
        });
    }

    //match correct answer to element name
    self.getElm = function(correct){
        if(correct == 0)
            return "#answer-one"
        if(correct == 1)
            return "#answer-two"
        if(correct == 2)
            return "#answer-three"
        if(correct == 3)
            return "#answer-four"
    }

 	// Executes the proceedure of a correct answer guess, moving
 	// the player to the next level (or winning the game if all
 	// levels have been completed)
 	self.rightAnswer = function(elm) {
 		$("#" + elm).slideUp('slow', function() {
 			startSound('right', false);
 			$("#" + elm).css('background', 'green').slideDown('slow', function() {
 				self.money($(".active").data('amt'));
 				if(self.level() + 1 > 15) {
	 				$("#game").fadeOut('slow', function() {
                        console.log("History", self.history);
                        self.showReport();
	 					$("#game-over").html('You Win!<br /><button onclick=\"window.location.replace(\'/\')\">Play again?</button>');
	 					// self.showReport();
	 				});
 				} else {
 					self.level(self.level() + 1);
                    sessionStorage.setItem("currentLevel",self.level());
 					$("#" + elm).css('background', 'none');
			 		$("#answer-one").show();
			 		$("#answer-two").show();
			 		$("#answer-three").show();
			 		$("#answer-four").show();
			 		self.transitioning = false;
 				}
 			});
 		});
 	}

 	// Executes the proceedure of guessing incorrectly, letting the player try again.
 	self.wrongAnswer = function(elm) {
        $("#"+elm).slideUp('slow', function() {
            startSound('wrong', false);
            $("#"+elm).css('background', 'red').slideDown('slow', function() {
                const mode = getGameMode();
                if (mode === "original") {

                    $("#game").fadeOut('slow', function() {
                        $("#game-over").fadeIn('slow');
                            sessionStorage.removeItem("currentGame");
                            sessionStorage.removeItem("currentLevel");
                    });

                    self.transitioning = false;
                    return;
                }
                $("#"+elm).css('background', 'none');
                $("#answer-one, #answer-two, #answer-three, #answer-four").show();
                self.transitioning = false;
            });
        });
 	}

 	// Gets the money formatted string of the current won amount of money.
 	self.formatMoney = function() {
	    return self.money().money(2, '.', ',');
	}  
    
    self.showReport = function() {

        console.log("Saving game results...");

        fetch('/save-results/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                finalMoney: self.money(),
                difficulty: getGameMode(),
                history: self.history
            })
        })
        .then(response => response.json())
        .then(data => {

            console.log("Saved", data);
            loadLifetimeStats();
            sessionStorage.removeItem("currentGame");
            sessionStorage.removeItem("currentLevel");

        })
        .catch(error => {
            console.error("Save failed:", error);
        });
    };

function setGameMode() {
    var mode = document.querySelector(
        'input[name="gameMode"]:checked'
    ).value;

    localStorage.setItem("gameMode", mode);
}

function loadLifetimeStats() {

    fetch('/get-results/')
        .then(response => response.json())
        .then(data => {

            var html = "";

            for (var g = 0; g < data.length; g++) {

                var game = data[g];
                var date = new Date(game.played_at);

                var timestamp = isNaN(date.getTime())
                    ? game.played_at
                    : date.toLocaleString();

                var correct = 0;

                for (var i = 0; i < game.history.length; i++) {
                    if (game.history[i].isCorrect) {
                        correct++;
                    }
                }

                var totalQuestions = game.history.length;
                var percent = totalQuestions > 0
                    ? Math.round((correct / totalQuestions) * 100)
                    : 0;

                html += "<details " + (g === data.length - 1 ? "open" : "") + ">";
                html += "<summary>";
                html += "Game " + (g + 1);
                html += " - " + timestamp;
                html += " - Score: " + percent + "%";
                html += "</summary>";

                html += "<ul>";

                for (var i = 0; i < game.history.length; i++) {

                    var h = game.history[i];

                    html += "<li>";
                    html += "<b>Q:</b> " + h.question + "<br>";
                    html += "<b>Your Answer:</b> " + h.selected + "<br>";
                    html += "<b>Result:</b> " + (h.isCorrect ? "Correct" : "Wrong");
                    html += "</li><br>";
                }

                html += "</ul>";
                html += "</details><hr>";
            }

            $("#report-content").html(html);

            $("#game").fadeOut('slow', function() {
                $("#report").fadeIn('slow');
            });
        });
    }
}

// Executes on page load, bootstrapping
// the start game functionality to trigger a game model
// being created
$(document).ready(function() {

    console.log("Ready function worked");

    let storedGame = sessionStorage.getItem("currentGame");

    if (!storedGame) {
        console.error("No game data found");
        return;
    }

    let data = JSON.parse(storedGame);
    console.log("Loaded from sessionStorage:");
    console.log(data);
    ko.applyBindings(
        new MillionaireModel(data.games[0])
    );

    startSound('background', true);
    $("#game").fadeIn('slow');
    console.log("Game loaded");
});