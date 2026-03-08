import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Hide main tkinter window
Tk().withdraw()

# Open file chooser
file_path = askopenfilename(title="Select an Ingredient Image")

# Load model
model = tf.keras.models.load_model("ingredient_model.h5")

# Load and prepare image
img = image.load_img(file_path, target_size=(224, 224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = img_array / 255.0

# Predict
prediction = model.predict(img_array)

class_names = ['Onion', 'Potato', 'Tomato']

predicted_class = class_names[np.argmax(prediction)]
confidence = np.max(prediction) * 100

print("\n🔍 Prediction Result:")
print("Ingredient:", predicted_class)
print("Confidence: {:.2f}%".format(confidence))
