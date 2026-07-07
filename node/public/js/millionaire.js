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
		// play() returns a promise that rejects if the browser blocks
		// autoplay before the first user interaction - ignore that.
		soundHandle.play().catch(function() {});
	}
}

// Game options come from the URL: /game?selection=1&mode=practice&player=Alice
var urlParams = new URLSearchParams(window.location.search);
var gameSelection = urlParams.get("selection");
var gameMode = urlParams.get("mode") === "practice" ? "practice" : "original";
var playerName = (urlParams.get("player") || "").trim();

/**
* The View Model that represents one game of
* Who Wants to Be a Millionaire.
*
* @param data the question bank to use
*/
var MillionaireModel = function(data) {
	var self = this;
	var help = -1

	// Answer log for the post-game report
	this.history = [];

	// The 15 questions of this game
	this.questions = data.questions;

	// A flag to keep multiple selections
	// out while transitioning levels
	this.transitioning = false;

	// The current money obtained
	this.money = new ko.observable(0);

	// The current level(starting at 1)
	this.level = new ko.observable(1);

	// The three the user can use to
	// attempt to answer a question (1 use each)
	this.usedFifty = new ko.observable(false);
	this.usedPhone = new ko.observable(false);
	this.usedAudience = new ko.observable(false);

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

		//Random to decide whether to use 80% or 50/50
		var rand = Math.random()
		var elm = this.questions[self.level() - 1].correct

		//80% correct option
		if(rand <= .50) {
			rand = Math.random()
			var chosenNum = rand <= .80 ? elm : getRandomInt(0, 3);
			help = 1
			var textToDisplay = "Your friend thinks the correct answer is " + "ABCD"[chosenNum];
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
			$("#display-help").fadeIn('slow');
			document.getElementById("display-help").innerHTML = "Your friend thinks one of these is the correct answer.";
		}
	}

	function getRandomInt(min, max) {
		min = Math.ceil(min);
		max = Math.floor(max);
		return Math.floor(Math.random() * (max - min + 1)) + min;
	}

	//Uses the audience option
	self.audience = function(item, event) {
		if(self.transitioning)
			return;
		$(event.target).fadeOut('slow');

		var rand = Math.random()
		var elm = this.questions[self.level() - 1].correct
		var chosenNum = rand <= .75 ? elm : getRandomInt(0, 3);

		help = 1
		$("#display-help").fadeIn('slow');
		document.getElementById("display-help").innerHTML = "The audience thinks the correct answer is " + "ABCD"[chosenNum];
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
			help = -1
		}

		var isCorrect = self.questions[self.level() - 1].correct == index;
		self.logAnswer(index, isCorrect);

		if(isCorrect) {
			self.rightAnswer(elm);
		} else {
			self.wrongAnswer(elm);
		}
	}

	// Records the player's choice for the post-game report
	self.logAnswer = function(index, isCorrect) {
		var q = self.questions[self.level() - 1];
		self.history.push({
			question: q.question,
			selected: q.content[index],
			correct: q.content[q.correct],
			difficulty: q.difficulty,
			isCorrect: isCorrect
		});
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
					self.endGame(true);
				} else {
					self.level(self.level() + 1);
					$("#" + elm).css('background', 'none');
					$("#answer-one, #answer-two, #answer-three, #answer-four").show();
					self.transitioning = false;
				}
			});
		});
	}

	// Executes the proceedure of guessing incorrectly. In practice mode
	// the player may retry the question; in the original mode the game ends.
	self.wrongAnswer = function(elm) {
		$("#" + elm).slideUp('slow', function() {
			startSound('wrong', false);
			$("#" + elm).css('background', 'red').slideDown('slow', function() {
				if (gameMode === "original") {
					self.endGame(false);
					return;
				}
				$("#" + elm).css('background', 'none');
				$("#answer-one, #answer-two, #answer-three, #answer-four").show();
				self.transitioning = false;
			});
		});
	}

	// Ends the game (win or lose), saves the results, and shows the
	// post-game report. Losses are recorded too, so the AI feedback
	// sees the full picture - the original only saved wins.
	self.endGame = function(won) {
		$("#report-title").text(won ? "You Win!" : "Game Over");
		$("#report-player").text(playerName + "'s game history");

		fetch('/api/results', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				player: playerName,
				selection: gameSelection,
				mode: gameMode,
				won: won,
				finalMoney: self.money(),
				history: self.history
			})
		})
		.then(function(response) { return response.json(); })
		.catch(function(error) { console.error("Save failed:", error); })
		.then(function() { self.showReport(); });
	}

	// Builds the lifetime stats report from this player's saved games
	self.showReport = function() {
		fetch('/api/results?player=' + encodeURIComponent(playerName))
			.then(function(response) { return response.json(); })
			.then(function(data) {
				var html = "";

				for (var g = 0; g < data.length; g++) {
					var game = data[g];
					var date = new Date(game.played_at);
					var timestamp = isNaN(date.getTime()) ? game.played_at : date.toLocaleString();

					var correct = 0;
					for (var i = 0; i < game.history.length; i++) {
						if (game.history[i].isCorrect) correct++;
					}
					var percent = game.history.length > 0
						? Math.round((correct / game.history.length) * 100)
						: 0;

					html += "<details " + (g === data.length - 1 ? "open" : "") + ">";
					html += "<summary>Game " + (g + 1) + " - " + timestamp + " - Score: " + percent + "%</summary>";
					html += "<ul>";
					for (var i = 0; i < game.history.length; i++) {
						var h = game.history[i];
						html += "<li>";
						html += "<b>Q:</b> " + h.question;
						if (h.difficulty) html += ' <span class="difficulty-tag ' + h.difficulty + '">' + h.difficulty + '</span>';
						html += "<br>";
						html += "<b>Your Answer:</b> " + h.selected + "<br>";
						html += "<b>Result:</b> " + (h.isCorrect ? "Correct" : "Wrong");
						html += "</li><br>";
					}
					html += "</ul></details><hr>";
				}

				$("#report-content").html(html);
				$("#game").fadeOut('slow', function() {
					$("#report").fadeIn('slow');
				});
			})
			.catch(function(error) {
				console.error("Loading report failed:", error);
				$("#game").fadeOut('slow', function() {
					$("#report").fadeIn('slow');
				});
			});
	}

	// Gets the money formatted string of the current won amount of money.
	self.formatMoney = function() {
		return self.money().money(2, '.', ',');
	}
};

// Executes on page load: fetches the questions for the selected game
// from the API (dynamic games show a loading screen while the AI
// generates them), then bootstraps the game model.
$(document).ready(function() {
	if (!gameSelection || !playerName) {
		window.location.replace('/');
		return;
	}

	// The AI Feedback button reviews this player's history specifically
	$("#feedback-link").on('click', function() {
		window.location.href = '/feedback?player=' + encodeURIComponent(playerName);
	});

	if (gameSelection.indexOf('dynamic') === 0) {
		$("#loading-text").text("Generating your questions with AI - this can take a little while...");
	}
	$("#loading").show();

	fetch('/api/game?selection=' + encodeURIComponent(gameSelection))
		.then(function(response) {
			return response.json().then(function(data) {
				if (!response.ok) throw new Error(data.error || 'Failed to load game');
				return data;
			});
		})
		.then(function(data) {
			ko.applyBindings(new MillionaireModel(data));
			$("#loading").hide();
			startSound('background', true);
			$("#game").fadeIn('slow');
		})
		.catch(function(error) {
			$("#loading-text").text(error.message);
			$("#loading .spinner").hide();
			$("#loading-back").show();
		});
});
