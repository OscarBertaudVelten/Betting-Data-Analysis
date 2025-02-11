import requests
import csv
from io import StringIO
from collections import defaultdict
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Class and function definitions remain the same
class Bet:
    def __init__(self, date, league, team_a, team_b, bet, result, odds, stake, gain, win_lose, total_at_time):
        self.date = date
        self.league = league
        self.team_a = team_a
        self.team_b = team_b
        self.bet = bet
        self.result = result
        self.odds = float(odds)
        self.stake = float(stake)
        self.gain = float(gain)
        self.win_lose = win_lose
        self.total_at_time = float(total_at_time)

    def __repr__(self):
        return (f"{self.date}, {self.league}, {self.team_a}, {self.team_b}, "
                f"{self.bet}, {self.result}, {self.odds}, {self.stake}, {self.gain}, "
                f"{self.win_lose}, {self.total_at_time}")

SHEET_URL = "https://docs.google.com/spreadsheets/d/1qdIxJxt7z-HuCqwLlI8Tv1Wt-tUXeFKWr_E7HF-tTXE/export?format=csv"
BETS = []

def extractData():
    response = requests.get(SHEET_URL)
    response.raise_for_status()  # Ensure request was successful

    csv_content = StringIO(response.text)
    csv_reader = csv.reader(csv_content)

    next(csv_reader)  # Skip empty row
    next(csv_reader)  # Skip header row

    for row in csv_reader:
        bet = Bet(
            date=row[0],
            league=row[1],
            team_a=row[2],
            team_b=row[3],
            bet=row[4],
            result=row[5],
            odds=float(row[6]),
            stake=float(row[7]),
            gain=float(row[8]),
            win_lose=row[9],
            total_at_time=float(row[10])
        )
        BETS.append(bet)

def analyzeByLeague():
    leagues = defaultdict(list)

    # Group bets by league
    for bet in BETS:
        leagues[bet.league].append(bet)

    return leagues

# Tkinter app setup
def create_app():
    root = tk.Tk()
    root.title("Bet Data Analysis")

    # Frame for table
    table_frame = ttk.Frame(root)
    table_frame.pack(fill=tk.BOTH, expand=True)

    # Frame for chart
    chart_frame = ttk.Frame(root)
    chart_frame.pack(fill=tk.BOTH, expand=True)

    # Extract data
    extractData()
    leagues = analyzeByLeague()

    # Set up table
    columns = ("League", "Bets", "Stake", "Gain", "Wins", "Losses")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    tree.pack(fill=tk.BOTH, expand=True)

    for col in columns:
        tree.heading(col, text=col)

    for league, bets in leagues.items():
        total_bets = len(bets)
        total_stake = sum(bet.stake for bet in bets)
        total_gain = sum(bet.gain for bet in bets) - total_stake
        wins = sum(1 for bet in bets if bet.win_lose == "W")
        losses = total_bets - wins
        tree.insert("", tk.END, values=(league, total_bets, f"{total_stake:.2f}", f"{total_gain:.2f}", wins, losses))

    # Plot chart
    def plot_chart():
        league_names = list(leagues.keys())
        wins = [sum(1 for bet in bets if bet.win_lose == "W") for bets in leagues.values()]
        losses = [len(bets) - win for bets, win in zip(leagues.values(), wins)]

        fig, ax = plt.subplots()
        ax.bar(league_names, wins, label="Wins", alpha=0.7)
        ax.bar(league_names, losses, label="Losses", alpha=0.7, bottom=wins)

        ax.set_xlabel("Leagues")
        ax.set_ylabel("Number of Bets")
        ax.set_title("Bets by League: Wins and Losses")
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    plot_button = ttk.Button(root, text="Show Chart", command=plot_chart)
    plot_button.pack()

    root.mainloop()

# Run the app
if __name__ == "__main__":
    create_app()
