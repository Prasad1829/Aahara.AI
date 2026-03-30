# AaharaAI Panel Preparation

## 1. Two-Minute Panel Speech

Good morning everyone. My project is **AaharaAI**, an AI-powered recipe identification and recommendation system. The main problem I wanted to solve is very practical: many people have ingredients at home, but they are unsure what they can cook from them. This leads to confusion, poor meal planning, and sometimes even food waste.

To solve this, I built a full-stack application that helps users discover recipes based on the ingredients they already have. The system supports three input methods: users can upload an ingredient image, select vegetables visually, or enter ingredients manually. Based on that input, the system detects ingredients and recommends suitable recipes.

What makes this project stronger than a basic recipe app is the hybrid AI pipeline behind it. For image-based input, I use a CNN-based ingredient classifier. For packet labels or text-heavy images, I use OCR to extract ingredient names. I also support additional vision-based signals for improved multi-ingredient detection. After detection, the ingredients are normalized and passed to a recommendation engine that compares them with recipe data and ranks the best matches.

On the technical side, the frontend is built with React and Vite, the backend is built with FastAPI, and the database layer uses SQLAlchemy. The application also supports authentication, wishlist management, history tracking, and AI-generated cooking instructions.

One important part of this project is that I focused on real-world issues, not just ideal conditions. I handled multiple image formats, OCR noise, inconsistent ingredient names, and fallback behavior when external AI services are unavailable.

Overall, AaharaAI demonstrates how machine learning, OCR, backend engineering, and frontend development can be integrated into a practical and user-friendly solution that helps users cook smarter with the ingredients they already have.

Thank you.

## 2. Five-Minute Full Demonstration Script

### Opening: 30-40 seconds

Good morning everyone. Today I am presenting **AaharaAI**, an ingredient-based intelligent recipe identification and recommendation system.

The motivation behind this project is simple: many people open their kitchen, see available ingredients, but still do not know what to cook. My project solves this by allowing the user to provide ingredients in different ways and then receive recipe recommendations automatically.

This is not only a frontend project or only an ML project. It is a complete full-stack system that combines **React frontend, FastAPI backend, OCR, machine learning, database integration, and AI-based instruction generation**.

### Demo Step 1: Landing and Authentication - 30 seconds

First, I will show the landing page and authentication flow.

The application begins with a branded splash and landing experience. From here, the user can sign up or log in. Authentication is protected, so only logged-in users can access the main dashboard and personalized features like wishlist and history.

If the panel asks why authentication is needed, say:

Authentication is important because the project includes personalized features such as saved recipes, user history, and profile-level access.

### Demo Step 2: Dashboard - 30-40 seconds

After login, the user reaches the dashboard. Here the project provides three different ways to give ingredient input:

1. **Upload Image** for AI-based ingredient detection from a photo
2. **Select Vegetables** for visual selection from a list
3. **Manual Entry** for direct text input

This is one of the strengths of the system because it improves usability. Different users prefer different input methods, so the app does not depend on only one interaction style.

### Demo Step 3: Upload Image Flow - 1.5 minutes

Now I will demonstrate the main AI flow using **Upload Image**.

The user uploads an ingredient image. On the backend, the system first validates the file type and file size. It supports multiple formats such as JPG, PNG, WebP, AVIF, BMP, and TIFF. If necessary, the image is converted into JPG for processing. This makes the system more practical for real-world usage.

After validation, the image goes through a **hybrid detection pipeline**:

1. A CNN-based model predicts the ingredient from the image.
2. OCR extracts text if the image contains packet labels or printed ingredient information.
3. Additional vision-based detection can help in multi-ingredient recognition.
4. The outputs are normalized so that inconsistent ingredient names become standardized.

This hybrid design is important because a single method is often not enough. Pure image classification is strong for visible raw ingredients, while OCR works better for text-heavy packets. Combining them improves robustness.

Once the ingredients are finalized, the recommendation engine uses them to search recipe data and return:

1. Recommended recipes with stronger matches
2. Additional recipes with partial matches

I would point out here that the matching logic is designed carefully. Common pantry items like oil, salt, and spices are treated differently so they do not dominate the scoring. This gives more realistic recipe recommendations.

### Demo Step 4: Recipe Details and AI Assistance - 50 seconds

Next, I open a recipe detail page.

Here the user can see the recipe name, ingredient list, cooking time, and generated cooking instructions. The instruction service supports AI-generated guidance, including preparation steps, cooking steps, difficulty, serving details, tips, and nutrition notes.

This extends the system from simple ingredient detection into actual cooking assistance. So the app does not stop at “what can I make,” but also helps with “how do I make it.”

### Demo Step 5: Alternate Inputs - 40 seconds

Now I briefly show the other two input methods.

The **Select Vegetables** page is useful for users who prefer tapping items visually instead of typing. The **Manual Entry** page is the fastest option when the user already knows their ingredients.

These alternate flows improve accessibility and make the system usable even when image recognition is not needed.

### Demo Step 6: Personalization Features - 30-40 seconds

Finally, I show the **wishlist** and **history** pages.

Wishlist allows users to save recipes they want to try later. History tracks recipes the user has already viewed. These features make the project feel like a real product instead of just a technical prototype.

### Closing: 30-40 seconds

To conclude, AaharaAI is a practical full-stack AI application that combines ingredient detection, OCR, recommendation logic, and cooking assistance in one system.

Its key strengths are:

1. Multiple user input methods
2. Hybrid ML + OCR + vision-based ingredient detection
3. Realistic recipe recommendation logic
4. Personalized user features
5. Modular and scalable architecture

This project demonstrates both technical depth and real-world usability.

Thank you.

## 3. Expected Viva Questions With Tailored Answers

### 1. What is the main objective of your project?

The main objective of AaharaAI is to help users identify available ingredients and recommend suitable recipes based on those ingredients. The goal is to reduce cooking decision time, improve ingredient usage, and provide practical cooking assistance through AI and full-stack technologies.

### 2. Why did you choose this project?

I chose this project because it solves a relatable real-world problem. Many people have ingredients at home but do not know what recipe to make from them. It also gave me the opportunity to integrate machine learning, OCR, backend APIs, frontend UI, and database features into one complete application.

### 3. What is unique about your project?

The unique part of the project is the **hybrid detection pipeline**. Instead of relying only on image classification, I combined CNN-based ingredient prediction, OCR-based text extraction, and additional vision-based signals. This improves reliability for different image types such as raw ingredient photos and food packet labels.

### 4. What technologies did you use in this project?

I used **React and Vite** for the frontend, **FastAPI** for the backend, **SQLAlchemy** for the database layer, **TensorFlow/Keras** for the CNN model, **OpenCV and Tesseract OCR** for text extraction and preprocessing, and AI service integration for recipe instruction generation.

### 5. Why did you use FastAPI for the backend?

I used FastAPI because it is lightweight, fast, and well suited for REST API development. It also provides clear routing, easy request validation, and good support for modular backend design.

### 6. Why did you use React for the frontend?

I used React because it supports reusable components, client-side routing, and smooth user interactions. Since the project has multiple pages like dashboard, upload, manual entry, wishlist, history, and profile, React was a good fit for building a responsive user experience.

### 7. How does the image upload pipeline work?

When the user uploads an image, the backend validates the file type and size, stores it temporarily, and converts it to JPG if needed. Then the system runs ML-based ingredient prediction, OCR extraction, and optional vision-based detection. The outputs are normalized and used to generate recipe recommendations.

### 8. Why did you use OCR in a recipe project?

OCR is useful because ingredients are not always visible as raw vegetables or food items. Sometimes the user may upload a packet label or printed ingredient list. OCR helps extract text from those images, making the system useful in more real-world scenarios.

### 9. What kind of ML model did you use?

I used a CNN-based classifier for ingredient recognition, built using TensorFlow/Keras. The project also includes dataset preparation, augmentation, and model training utilities.

### 10. Why is a single model not enough?

A single model may perform well only for one type of input. For example, image classification works well for visible ingredients, but it may fail on text-heavy packet images. OCR works well on text but not on natural object images. That is why I used a hybrid approach.

### 11. How does the recommendation engine work?

The recommendation engine compares detected ingredients with stored recipe ingredients. It calculates a match score and ranks recipes into recommended and additional groups. It also treats optional pantry items separately so that recipe scoring reflects the important ingredients more realistically.

### 12. Why did you separate pantry ingredients like oil and salt?

Ingredients like oil, salt, and basic spices are common in many recipes, so if they are treated as major ingredients, the recommendation quality becomes unrealistic. Separating them helps the system focus on significant ingredients like paneer, tomato, chicken, fish, or potato.

### 13. What database features are included?

The project includes recipe storage, ingredient mapping, user authentication data, wishlist functionality, and history tracking. These features help support both the recommendation engine and user personalization.

### 14. What is ingredient normalization, and why is it needed?

Ingredient normalization means converting different forms of the same ingredient into a consistent standard name. This is needed because ML, OCR, or text input may produce variations. Without normalization, recipe matching becomes inconsistent and less accurate.

### 15. What challenges did you face?

The main challenges were OCR noise, varied image formats, inconsistent ingredient naming, and making recipe matching realistic. I also had to handle cases where AI services may not be available.

### 16. How did you solve OCR noise?

I solved OCR noise by using preprocessing, text cleaning, filtering rules, and ingredient normalization. This helped remove unrelated packaging text and keep only useful ingredient terms.

### 17. How did you handle multiple image formats?

I allowed multiple extensions, validated them during upload, and converted unsupported working formats into JPG before processing. This improved compatibility for real-world uploads.

### 18. How is your project modular?

The project is divided into phases and modules. There are separate services for OCR, ML, instruction generation, recommendation logic, image processing, and backend routes. This makes the application easier to maintain, test, and extend.

### 19. What are the main user features?

The main user features are signup/login, image upload-based detection, visual ingredient selection, manual ingredient entry, recipe recommendations, recipe detail view, wishlist, history, profile, and settings.

### 20. Does your project support vegetarian and non-vegetarian filtering?

Yes. The recommendation logic supports preference filtering so the user can request vegetarian or non-vegetarian recipes.

### 21. What happens if AI services are not available?

The project is designed to fail gracefully. Instead of crashing, it returns friendly fallback responses. This is important for maintaining a stable user experience.

### 22. How does your project reduce food waste?

It helps users make recipes from ingredients already available at home. This encourages better ingredient utilization and reduces the chance that ingredients are left unused and wasted.

### 23. What is the real-world value of this project?

The real-world value is that it combines convenience, intelligent recommendation, and cooking support into one application. It can help students, working professionals, and families make faster and better meal decisions.

### 24. What improvements can be made in the future?

Future improvements could include larger ingredient datasets, support for more cuisines, better multi-object detection, voice input, barcode-based packet scanning, nutrition personalization, and deployment to cloud platforms for production use.

### 25. If the panel asks, “What did you personally learn from this project?” what should you say?

This project improved my understanding of full-stack development, API design, authentication, OCR, image processing, ML integration, recommendation systems, and modular software architecture. It also taught me how to handle real-world edge cases rather than only ideal technical scenarios.

### 26. If the panel asks, “What was your contribution?” what should you say?

I worked on the end-to-end integration of the system, including the frontend flow, FastAPI backend structure, ingredient detection pipeline, recommendation logic, and user-focused features like authentication, wishlist, and history. I also worked on handling edge cases, testing, and documentation.

### 27. If the panel asks, “Why should we consider this a strong project?” what should you say?

Because it is not a single-feature prototype. It is a complete, user-oriented, full-stack AI system with multiple input methods, hybrid intelligence, recommendation logic, and personalized features. It shows both technical depth and practical usability.

## 4. Quick Final Reminders Before the Panel

1. Start with the problem, not the technology.
2. Speak in simple and confident language.
3. Use words like modular, scalable, hybrid, practical, and real-world.
4. Highlight your contribution clearly.
5. If the demo fails at any step, explain the expected flow confidently.
6. End by connecting the project to user benefit and real-world impact.
