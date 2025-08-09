# AutoGen Society of Mind – Disaster Management Scenario

## 📌 Project Description

This project demonstrates an **AutoGen Society of Mind (SoM)** approach to disaster management during a major flood in Bihar.
The system uses multiple agents arranged into **Inner Teams** and **Outer Teams** to coordinate planning, risk analysis, resource allocation, and communication with human oversight.

The **UserProxyAgent** acts as the main interface for human feedback and decision-making.

---

## 📂 Project Structure

* main.py → Main execution file
* requirements.txt → Required Python dependencies
* flowchart.png → Flowchart diagram showing the Society of Mind architecture
* README.md → Documentation file

---

## 🚀 How to Run the Code

### 1. Clone the repository

git clone [https://github.com/sxnskrxtiiiii/Autogen-Assignment0](https://github.com/sxnskrxtiiiii/Autogen-Assignment0)
cd Autogen-Assignment0

### 2. Install dependencies

pip install -r requirements.txt

### 3. Add your API key

Create a `.env` file in the root folder and add your key:
OPENAI_API_KEY=your_api_key_here


### 4. Run the project

python main.py

---

## 📊 Disaster Scenario Data

**Locations:**

* Affected districts: 12–15 districts, including Patna, Bhagalpur, Munger, Khagaria, and Begusarai
* Worst-hit areas: North Bihar, particularly along the Ganges river (Patna, Bhagalpur, Munger)
* Flood-prone rivers: Kosi, Gandaki, Burhi Gandak

**Counts:**

* Estimated displaced people: 500,000+
* Affected population: 1.5–2 million
* Deaths: 20–30
* Injured: 50–100

**Infrastructure Damage:**

* Roads damaged: 100–200 km
* Bridges damaged: 10–20
* Power outages: 50–70% affected
* Telecommunication: 20–30% damaged
* Healthcare: 10–20 facilities affected
* Education: 50–100 institutions affected

**Other Indicators:**

* Crop damage: 10,000–20,000 hectares (₹500–1000 crore loss)
* Livestock affected: 10,000–20,000 animals
* Relief camps: 100–200 camps, sheltering 50,000–100,000 people

---

## 🧠 AutoGen Society of Mind Architecture

The system is designed with:

* **Inner Teams** → Specialists focusing on risk assessment, resource allocation, and communication
* **Outer Team** → Manages multiple inner teams and ensures coordination
* **UserProxyAgent** → Facilitates human-in-the-loop feedback

---

## 📌 Flowchart

![Flowchart](flowchart.png)

---
