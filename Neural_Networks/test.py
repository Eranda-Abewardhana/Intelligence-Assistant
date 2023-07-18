import numpy as np
from tensorflow import keras
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

# Define the training data
inputs = np.array([ [0, 0], [0, 1], [1, 0], [1, 1] ])
normalized_inputs = scaler.fit_transform(inputs)

outputs = np.array([ [0, 0, 0], [1, 0, 1], [1, 0, 1], [0, 1, 0] ])

# Create the ANN model
model = keras.models.Sequential()
model.add(keras.layers.Dense(units=8, activation='relu', input_dim=2))
model.add(keras.layers.Dense(units=8, activation='relu'))
model.add(keras.layers.Dense(units=8, activation='tanh', input_dim=2))
# model.add(keras.layers.Dense(units=8, activation='relu', input_dim=2, kernel_regularizer=keras.regularizers.l2(0.01)))
model.add(keras.layers.Dense(units=3, activation='sigmoid'))


# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
# model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(normalized_inputs, outputs, epochs=2000, batch_size=4)

# Test the model
test_input = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
predictions = model.predict(test_input)
print(predictions)
