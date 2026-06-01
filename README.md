# Proiect-Facultate-Python
# 🌱 EcoSmart Ultimate

Aceasta este o aplicație web construită cu Python și Streamlit pentru monitorizarea, simularea și analiza costurilor de energie și apă. (Proiect de facultate).

## ⚙️ Cum să rulezi aplicația pe calculatorul tău

Pentru a rula acest proiect local, urmează acești pași:

1. **Descarcă proiectul:**
   Clonează acest repository sau descarcă-l sub formă de arhivă ZIP și extrage-l într-un folder.

2. **Instalează dependințele:**
   Deschide un terminal (Command Prompt / PowerShell) în folderul proiectului și rulează comanda:
   ```bash
   pip install -r requirements.txt
3.După ce librăriile s-au instalat, rulează comanda de mai jos în același terminal:
   ```bash
   streamlit run app.py 
   ```
(Notă: Asigură-te că fișierul principal se numește app.py. Dacă l-ai numit altfel, înlocuiește numele în comandă).
Aplicația se va deschide automat într-un tab nou în browserul tău web!

## 🎨 Configurare Interfață (Tema)

Această aplicație este proiectată cu o interfață personalizată (Light Mode) pentru a asigura o lizibilitate optimă a graficelor Plotly și a contrastului textului. 

Pentru a preveni suprascrierea culorilor de către setările locale ale browserului sau ale sistemului de operare (ex. Dark Mode forțat), aplicația folosește un fișier de configurare dedicat.

**Fișierul `.streamlit/config.toml` conține:**
```toml
[theme]
base="light"
```

Previzualizare:

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/2e776da0-37d9-410a-9dc5-10c0e7024f1f" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/b61eae11-c511-4f4b-8fa9-f4c5aa0ed1e4" />

<img width="1366" height="720" alt="image" src="https://github.com/user-attachments/assets/e4fbb43c-f063-4fff-b045-0ba1af6adad2" />





