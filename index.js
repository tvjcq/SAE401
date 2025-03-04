require("dotenv").config();

const express = require("express");
const myDB = require("./src/sgbd/config.js");
require("./src/sgbd/models.js");

const routerPlayers = require("./src/routes/");
const routerChampionships = require("./src/routes/");
const routerWins = require("./src/routes/");
const routerPlays = require("./src/routes/");

const app = express();

app.use(express.json());

app.get("/", function (req, res) {
  res.send("Hello World");
});

app.use("/players", routerPlayers);
app.use("/championships", routerChampionships);
app.use("/wins", routerWins);
app.use("/plays", routerPlays);

const PORT = process.env.PORT || 3000;

myDB
  .sync({ alter: false, logging: false })
  .then(() => {
    console.log("Database synchronized");

    app.listen(PORT, () => {
      console.log(`Server run on http://localhost:${PORT}`);
    });
  })
  .catch((error) => {
    console.error("Failed to synchronize database:", error);
  });