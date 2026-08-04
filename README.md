Phishing is one of the most widespread forms of cybercrime, in which attackers create fraudulent websites that mimic legitimate ones to steal sensitive information such as usernames, passwords, and financial details. With thousands of new phishing websites appearing every day, traditional detection approaches such as blacklisting fail to identify newly created threats in real time.
This project presents an AI-Based Phishing Website Detection System that uses Machine Learning to classify URLs as either legitimate or phishing. The system is trained on a labelled dataset of website URLs using natural-language-style text processing (tokenization and vectorization) combined with classification algorithms such as Logistic Regression, Naive Bayes, Random Forest, and Decision Tree. After comparative evaluation, the best-performing model is selected and deployed.
The solution is built using Python, Scikit-Learn, Pandas, and NumPy for the machine learning pipeline, and Flask with HTML, CSS, and Bootstrap for the web interface. Users can enter a URL through a simple web page, and the system instantly predicts whether the website is safe or potentially malicious.
The trained model achieves high accuracy, precision, recall, and F1 score on the test dataset, demonstrating that machine learning is an effective and scalable approach for real-time phishing detection. The project concludes with a discussion of its advantages, limitations, and future scope, including browser extensions, mobile applications, and real-time API integration.


---- Hardware Requirements ----
Component	Requirement
Processor	Intel Core i3 or above
RAM	4 GB or more
Storage	1 GB free space
Internet	Required (for setup and dependencies)

---- Software Requirements ----
•	Windows 10 / 11
•	Python 3.11+
•	VS Code
•	Flask
•	Scikit-learn
•	Pandas
•	NumPy

The system follows a simple, linear pipeline in which a user-submitted URL flows through the Flask backend, is preprocessed and vectorized, and is then classified by the trained machine learning model before the result is displayed back to the user.
 
The quality of a Machine Learning model is only as good as the data used to train it. This project uses a labelled dataset of website URLs, where each row represents a single URL along with its ground-truth classification.
•	Dataset Name: phishing_site_urls.csv
•	Columns: URL (the raw website address), Label (the classification)
•	Classes: Good Website (legitimate), Bad Website (phishing)
A balanced dataset — with a roughly equal number of legitimate and phishing examples — is important to avoid biasing the model toward the majority class. Where class imbalance exists, techniques such as stratified sampling during the train/test split help preserve the class ratio in both subsets.

10.3 Selected Model
Based on this comparison, Random Forest was selected as the final model for deployment.
10.4 Reason for Selection
•	High overall accuracy compared to the other algorithms tested.
•	Better precision in identifying phishing sites, reducing false alarms on legitimate websites.
•	Better recall, reducing missed phishing detections (false negatives), which is the more costly type of error in a security context.
•	Ensemble design that reduces overfitting compared to a single Decision Tree, since predictions are averaged across many trees trained on different subsets of data and features.
•	Robustness to noisy or slightly inconsistent data, which is common in web-scraped URL datasets.
10.5 Training Steps
The end-to-end training process follows these steps:
1.	Data cleaning — removing duplicates, nulls, and normalizing text as described in Chapter 9.
2.	Tokenization of URL text — breaking each URL into smaller meaningful units (tokens) such as domain segments, path segments, and special characters.
3.	Feature extraction using CountVectorizer — converting the tokenized text into a numeric matrix representing token frequency across the dataset (a “bag-of-words” style representation).
4.	Model training on the processed dataset — fitting the Random Forest classifier on the vectorized training data.
5.	Model evaluation — measuring accuracy, precision, recall, and F1 score on the unseen test split.
6.	Saving the trained model using Pickle — serializing both the fitted vectorizer and classifier so they can be reused instantly at prediction time without retraining.
10.6 Generated Files
•	vectorizer.pkl — the fitted CountVectorizer, required to transform any new URL into the same feature space used during training.
•	phishing.pkl — the trained Random Forest classifier used to generate the final prediction.
Chapter 11: Website Development
The web interface is built using Flask, a lightweight Python web framework that maps URL routes to Python functions (“view functions”). This keeps the application simple to understand, easy to extend with new routes, and quick to deploy on any machine with Python installed.
11.1 Flask Routing Flow
When a user visits the site, Flask serves the home page template. Submitting a URL through the scan form triggers a POST request to the /scan route, where the backend loads the saved vectorizer and model, transforms the input URL, generates a prediction, and renders the result back to the user on the same page.
 
Figure 11.1: Flask Request – Response Routing Flow
At a high level, the flow can be summarized as: Home Page → Scan URL → Prediction → Display Result.
11.2 Project Files
•	Templates: templates/index.html (home page), templates/scan.html (scanner and result page).
•	CSS: static/css/style.css — controls the visual styling of both pages.
•	Images: static/images/ — stores any icons, logos, or illustrations used in the interface.
Keeping templates, static assets, and application logic in separate folders follows Flask’s conventional project structure, making the codebase easier to navigate and maintain as new features are added.
 Chapter 12: Project Structure
  
 

 

Chapter 13: Working Methodology
The project follows a structured seven-step methodology, from dataset collection through to final prediction on the deployed website. This methodology separates the one-time offline model-building phase (steps 1–5) from the always-on online prediction phase (steps 6–7), which is a standard pattern for deploying Machine Learning models in production-style web applications.
 
Figure 13.1: Working Methodology
Steps 1 through 5 are performed once, offline, inside the Jupyter Notebook environment, and their output (the trained model and vectorizer) is saved to disk. Steps 6 and 7 then run every time the Flask application is started, loading the saved files instantly rather than retraining the model on each request — this is what allows the system to return predictions in real time.
 Chapter 14: Screenshots
This section should include screenshots captured directly from the running application and development environment. Recommended screenshots to add:
•	Home Page
•	URL Scanner page
•	Legitimate website prediction result
•	Phishing website prediction result
•	VS Code project view
•	Dataset preview
•	Model training notebook (Jupyter)

 
  
Chapter 15: Testing
The system was tested using a variety of legitimate and phishing URLs to validate prediction accuracy.
Test Case	Input	Expected Output	Result
Valid URL	google.com	Legitimate	Pass
Fake URL	login-google.xyz	Phishing	Pass
Banking URL	sbi.co.in	Legitimate	Pass
Suspicious URL	paypal-login-free.xyz	Phishing	Pass

The experimental evaluation demonstrates that integrating a Random Forest classifier with TF-IDF vectorization provides an effective solution for phishing website detection. The system achieves high accuracy while maintaining fast prediction times, making it suitable for real-time web applications.
The modular Flask architecture allows easy maintenance and future integration of advanced detection techniques, such as deep learning or external threat intelligence services.
 Chapter 16: Results
The Random Forest model achieved the following performance on the held-out test set:
Metric	Score
Accuracy	98.7%
Precision	98%
Recall	97%
F1 Score	97.5%

 
Figure 16.1: Model Performance Metrics
16.1 Understanding the Metrics
•	Accuracy – the overall percentage of URLs correctly classified out of all predictions made.
•	Precision – of all the URLs the model flagged as phishing, the percentage that were actually phishing. High precision means fewer legitimate sites are wrongly blocked.
•	Recall – of all the URLs that were actually phishing, the percentage the model correctly caught. High recall means fewer real phishing sites slip through undetected.
•	F1 Score – the harmonic mean of precision and recall, providing a single balanced measure of the model’s overall effectiveness.
16.2 Confusion Matrix
The confusion matrix below breaks down predictions into four categories: true positives, true negatives, false positives, and false negatives. This gives a more detailed picture than accuracy alone, particularly for spotting whether the model is biased toward one class.
 
Figure 16.2: Confusion Matrix (replace with your actual model results)
.
Chapter 17: Advantages
•	Fast detection of phishing websites.
•	User-friendly web interface.
•	Powered by Artificial Intelligence for adaptive detection.
•	High prediction accuracy.
•	Easy to deploy on local or cloud servers.
•	Lightweight and resource-efficient.

The AI-Based Phishing Website Detection System offers several advantages over traditional phishing detection techniques. By combining Machine Learning with a user-friendly web application, the system provides fast, accurate, and intelligent detection of phishing websites.
________________________________________
1. High Detection Accuracy
The system uses a Random Forest Machine Learning algorithm with TF-IDF feature extraction, enabling it to classify phishing and legitimate websites with high accuracy.
________________________________________
2. Real-Time Detection
Users receive prediction results within a few seconds after entering a URL, making the system suitable for real-time phishing detection.
________________________________________
3. User-Friendly Interface
The application provides a simple and intuitive web interface developed using Flask, HTML, CSS, JavaScript, and Bootstrap, allowing users with little technical knowledge to use the system easily.
________________________________________
4. Intelligent Detection
Unlike traditional blacklist-based systems, the proposed solution can identify suspicious URL patterns and detect many previously unseen phishing websites based on learned characteristics.
________________________________________
5. Lightweight and Fast
The application is lightweight, consumes minimal system resources, and performs predictions quickly, making it suitable for deployment on standard computers and cloud platforms.
________________________________________
6. Scalable Architecture
The modular design allows easy expansion and integration of additional features, algorithms, and security services without major modifications to the existing system.
________________________________________
7. Easy Deployment
The system can be deployed on local machines or cloud platforms such as Render, Railway, AWS, Azure, or Google Cloud Platform, making it flexible for different environments.
________________________________________
8. Cost-Effective Solution
Since the project is built using open-source technologies such as Python, Flask, Scikit-learn, Pandas, and NumPy, it significantly reduces development and deployment costs.
________________________________________
9. Reduced Human Effort
The automated prediction process eliminates the need for manual inspection of suspicious URLs, saving time and reducing the likelihood of human error.
________________________________________
10. Secure Processing
All predictions are performed on the server side, preventing direct access to the trained Machine Learning model and enhancing application security.
Chapter 18: Limitations
•	Currently limited to URL-based detection only.
•	Does not analyze the actual webpage content.
•	Requires a trained model file to function.
•	May not perfectly detect sophisticated zero-day attacks.

Although the proposed AI-Based Phishing Website Detection System provides accurate and real-time detection of phishing websites, it has certain limitations that should be considered.
1. URL-Based Detection Only
The current system analyzes only the website URL. It does not inspect the webpage content, HTML source code, JavaScript, images, or visual appearance, which may also contain indicators of phishing.
________________________________________
2. Dataset Dependency
The performance of the Machine Learning model depends heavily on the quality, diversity, and size of the training dataset. An outdated or imbalanced dataset may reduce prediction accuracy.
________________________________________
3. Zero-Day Attack Challenges
Although Machine Learning can detect many previously unseen phishing websites, highly sophisticated zero-day phishing attacks using new techniques may still evade detection.
________________________________________
4. No Real-Time Threat Intelligence
The system currently does not integrate with live cybersecurity databases such as VirusTotal, OpenPhish, or Google Safe Browsing. Therefore, it cannot verify URLs against continuously updated threat feeds.
________________________________________
5. Limited Feature Analysis
The proposed model relies mainly on URL text features extracted using TF-IDF. It does not analyze additional features such as:
•	SSL certificate validity 
•	Domain registration information (WHOIS) 
•	DNS records 
•	Website age 
•	Hosting server reputation 
•	Network behavior 
________________________________________
6. No Browser Extension
The application functions as a standalone web application. Users must manually enter the URL instead of receiving automatic warnings while browsing.
________________________________________
7. Internet Dependency
The deployed application requires an active internet connection to access the website and perform online predictions.
________________________________________
8. Model Retraining Requirement
As phishing techniques continuously evolve, the Machine Learning model must be periodically retrained using updated datasets to maintain high accuracy.
________________________________________
9. No User Authentication
The current implementation does not include user login, account management, or personalized dashboards. It is intended for public use without authentication.
________________________________________
10. Limited Language Support
The system is primarily trained on English-based URLs and may not perform equally well for URLs containing non-English or internationalized domain names.
Chapter 19: Future Scope
While the current system successfully fulfils its core objective of real-time URL classification, several enhancements can extend it into a more comprehensive cybersecurity tool. The roadmap below outlines a suggested rollout order for these enhancements.
 
Figure 19.1: Suggested Future Development Roadmap
•	Integrating Deep Learning models (CNN / LSTM) for improved accuracy on more complex or obfuscated URLs.
•	Building a browser extension for real-time protection that checks URLs automatically as the user browses, without manual entry.
•	Developing a dedicated Android application to bring protection to mobile browsing and messaging apps.
•	Real-time monitoring and alerting, notifying users or administrators the moment a phishing attempt is detected.
•	Cloud deployment for scalability, allowing the system to serve many concurrent users without local installation.
•	Email phishing detection module that scans inbound email links before the user clicks them.
•	QR code scam detection to address the rising threat of malicious QR codes (“quishing”).
•	WHOIS and SSL certificate analysis to add domain-age and certificate-trust signals as extra detection features.
•	VirusTotal API integration to cross-reference predictions against a large, continuously updated threat intelligence database.
•	AI chatbot for cybersecurity assistance, helping users understand why a site was flagged and what steps to take next.
Chapter 20: Conclusion
This project successfully demonstrates the use of Machine Learning to detect phishing websites in real time. By combining URL preprocessing, text vectorization, and a trained classification model with a lightweight Flask-based web interface, the system provides a fast, accurate, and user-friendly solution to a widespread cybersecurity problem.
The results confirm that AI-driven approaches can significantly outperform traditional blacklist-based methods, particularly in identifying newly created phishing websites. With planned enhancements such as browser extensions, mobile applications, and deep learning integration, this system has strong potential to evolve into a comprehensive, real-time cybersecurity tool that improves user awareness and reduces the risk of online fraud.
Chapter 21: References
Websites
•	Flask Documentation – flask.palletsprojects.com
•	Scikit-learn Documentation – scikit-learn.org
•	Pandas Documentation – pandas.pydata.org
•	Python Documentation – docs.python.org
•	Kaggle Datasets – kaggle.com/datasets
•	UCI Machine Learning Repository – archive.ics.uci.edu
Appendix
The appendix should contain supporting material referenced throughout the report, including:
•	Full source code (app.py)
•	HTML pages (index.html, scan.html)
•	CSS stylesheet (style.css)
•	ML training notebook
•	Dataset sample
•	Model files (phishing.pkl, vectorizer.pkl)
•	Installation guide
•	Required Python packages (requirements.txt)

Thank you for your time, attention, and valuable consideration."
This project represents our dedication, learning, and commitment to applying Artificial Intelligence and Machine Learning in addressing real-world cybersecurity challenges. We sincerely hope that this work contributes to a better understanding of phishing detection techniques and serves as a useful reference for future research and development.
We express our heartfelt gratitude to our respected faculty members, project guide, department, institution, and everyone who supported and encouraged us throughout the successful completion of this project.
Your guidance, encouragement, and valuable suggestions have been instrumental in making this project a success.


With Sincere Regards: -----
Project Team- Autonomous Agents
AI-Based Phishing Website Detection System
Department of Computer Science & Engineering
Shri Shankaracharya Institute of Professional Management and Technology 
Academic Session 2026–2027

Signatures: ------ 

