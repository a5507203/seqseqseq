

mle_lecture: str = '''
Lecture slide:
I am a lecturer. I am teaching the machine learning coure for research students. Please generate lecture slide for maximum likelihood estimation.
Note that:
1). Note that the lecture duration is 2 hour, so we need to generate 30 pages.
2). The slide should include motivation, problem and intuitive solution and detailed math equations.
3). Please make sure the the lecture have a good self-contain.

Output Format: Latex code
'''

nips_website: str = '''I want to create a website for the following conference:
1) Conference Name: The Thirty-Ninth Annual Conference on Neural Information Processing Systems (NIPS2025)
2) Date: Tuesday Dec 2nd through Sunday Dec 7th, 2025
3) Location: San Diego Convention Center, California, United States
4) Organizer: Neural Information Processing Systems Foundation
Please generate a detailed website structure and content for this conference. 
Ensure the content is professional, clear, and suitable for an international academic conference.

Output Format: html and css
'''



pac_tank: str = '''
Develop a single-player game that fuses mechanics from Pac-Man and Tank City.
The player controls a Pac-Man-like character navigating a maze, collecting pellets for points.
Enemy tanks act as ghost-like chasers, actively pursuing the player using basic AI pathfinding.

Enemy tanks can shoot bullets in four directions. Unlike traditional bullets, these bullets do not disappear—instead, they remain in the maze as collectible pellets.
The player must guide Pac-Man to eat as many of these bullets as possible to gain points and avoid tank power-ups.

If bullets are left uncollected, enemy tanks can absorb them to accelerate their shooting rate, making them more dangerous. Tanks can also switch between patrol and chase modes to track the player.

The player can collect special items that temporarily allow Pac-Man to eat enemy tanks for bonus points.

The game must support:
- Maze-based movement and pellet collection
- AI-controlled enemy tanks with patrol and chase behaviors
- Enemy tank shooting mechanics with persistent bullets
- Tank interaction with bullets (absorb and power-up)
- A GUI (using Pygame) showing the maze, player, enemies, pellets, and bullets
- Smooth animations and clear visual feedback

Sound effects are not required.

Output Format: python
'''


puzzle_game_electrical_circuits: str = '''
Create a casual browser puzzle game where players build electrical circuits from components.
- **Mechanics:** Drag-and-drop resistors, capacitors, and switches onto a grid to complete a target circuit.
- **Levels:** 20 puzzles of increasing difficulty.
- **Scoring:** Based on correctness and build time.
- **Tech:** HTML5 + CSS3 + vanilla JavaScript.

Output Format: HTML5 + CSS3 + vanilla JavaScript
'''



quiz_platform_metroidvania: str = '''
Title: Learn & Explore – Quiz-Gated Metroidvania Web Game

## Objective
Create a browser-based 2D side-scroll “metroidvania” where players unlock new movement abilities by answering mini-quizzes.

## Gameplay & World
- **Map:** Connected platform levels with locked gates:
  - **Fire Gate** – requires Fire Blast ability  
  - **Ice Gate** – requires Ice Dash ability  
  - **High Wall** – requires Double Jump ability  
- **Quiz Orbs:**  
  - Placed throughout levels.  
  - Collecting an orb pauses the game and displays a 3-question quiz (multiple choice A–D).

## Abilities & Quiz Rules
1. **Fire Blast** (breaks Fire Gates)  
2. **Ice Dash** (shatters Ice Gates)  
3. **Double Jump** (scales High Walls)  
4. **Quiz Mechanics:**  
   - Each orb quiz covers Math, History, or Science.  
   - **Success (3/3 correct):** grant matching ability, remove orb, unlock corresponding gates.  
   - **Failure:** orb remains for a later attempt.
5. No extra image or audio files are required

Output Format: HTML+CSS+JS
'''



snake_chess: str = '''
Develop a real-time arcade game that merges Snake with simplified chess tactics.
- **Player:** Controls a “snake” that grows by eating apples.
- **Chess Pieces:** Randomly spawning pawns, knights, and bishops move following their rules.
- **Mechanics:**
  1. If the snake’s head collides with an apple → length+1, score+10.
  2. If the snake’s head lands on a chess piece’s square → capture it: score+ piece value (pawn=5, knight=10, bishop=15), snake doesn’t grow.
  3. knights can shoot bullets. When player get shot, length-1. When length = 0 -> game over 
  4. Bullets will disappear when hit the edges
  5. Chess pieces move one step every second; if they collide with the snake’s body → game over.
  6. Board wraps around edges.
  7. No extra image files
- **UI:** Pygame window showing grid, snake, apples, chess pieces, current score, and “next piece spawn in Xs.” 

Output Format: python
'''


task_manager_rpg: str = '''
Build a desktop “RPG” where user’s real-world todo items become in-game quests.
- **Features:**
    1. User adds a task → appears as a “quest” on the map.
    2. Completing the task (marking done) triggers battle simulation against a monster.
    3. Success grants XP and loot; failure reduces HP.
    4. Shop uses gold to buy potions that restore HP.
    5. Audios are not needed
    6. No extra image files

Output Format: HTML+CSS+JS
'''


tetris_bjeweled: str = '''
Develop a game that fuses Tetris and Bejeweled mechanics. 
This game needs to add keyboard control function.
Falling tetrominoes should lock into a grid and transform into colored gems. 
The game must support both Tetris line-clearing and Bejeweled match-3 clearing, triggering chain reactions and bonus points. 
Include a GUI (using a framework like Pygame) that displays the game grid, current score, and next tetromino preview, along with smooth animations. 
No sound effects are needed.

Output Format: python
'''



travel_plan: str = '''
I need to attend the NIPS 2025 conference.  
- **Dates:** Tuesday, December 2nd through Sunday, December 7th, 2025.  
- **Location:** San Diego Convention Center, California, United States.  

I want to bring my husband and two children with me. We will be departing from Beijing. Please help me plan:  
1. **Flights** (round-trip options from Beijing to San Diego, considering family-friendly airlines and layovers).  
2. **Hotel** (family-friendly accommodations near the convention center, preferably with kitchenette or adjoining rooms).  
3. **Daily trip plan** (sightseeing and activities suitable for children, balanced with my conference schedule).  
4. **Cost estimate** (total budget breakdown for flights, hotel, meals, local transportation, and activities).  
Please provide me with LaTeX's itinerary plan.
'''



