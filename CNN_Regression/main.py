from data_loader_npy import DataLoader
from sklearn.model_selection import train_test_split
from model_regression import *
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.callbacks import EarlyStopping

import numpy as np

def get_train_dataset(energy_path : str, box_path : str, coord_path : str = None, force_path : str = None, virial_path : str = None) -> list:
    box_features = DataLoader(box_path)
    eneryg_target = DataLoader(energy_path)

    X1 = box_features.prepare_data()
    y = eneryg_target.prepare_data()

    X_train = None
    X_val = None
    y_train = None
    y_val = None
    scaler = StandardScaler()

    if not coord_path or not force_path or not virial_path:
        X_normalized = scaler.fit_transform(X1)
        X_normalized = X_normalized.reshape((X_normalized.shape[0], X_normalized.shape[1], 1))
        X_train, X_val, y_train, y_val = train_test_split(X_normalized, y, test_size=0.2, random_state=42)
    else:
        coord_features  = DataLoader(coord_path)
        force_features  = DataLoader(force_path)
        virial_features  = DataLoader(virial_path)

        X2 = coord_features.prepare_data()
        X3 = force_features.prepare_data()
        X4 = virial_features.prepare_data()

        X_combined = np.concatenate((X1, X2, X3, X4), axis=1)
        X_combined_normalized = scaler.fit_transform(X_combined)
        X_combined_normalized = X_combined_normalized.reshape(X_combined_normalized.shape[0], X_combined_normalized.shape[1], 1)
        X_train, X_val, y_train, y_val = train_test_split(X_combined_normalized, y, test_size=0.2, random_state=42)

    return X_train, X_val, y_train, y_val

def get_test_dataset(energy_path : str, box_path : str, coord_path : str = None , force_path : str = None, virial_path : str = None) -> list:
    box_features = DataLoader(box_path)
    eneryg_target = DataLoader(energy_path)
    X_test_1 = box_features.prepare_data()
    y_test = eneryg_target.prepare_data()

    scaler = StandardScaler()
    if not coord_path:
        X_normalized = scaler.fit_transform(X_test_1)
        X_normalized = X_normalized.reshape((X_normalized.shape[0], X_normalized.shape[1], 1))
        return X_normalized, y_test

    else:
        coord_features  = DataLoader(coord_path)
        force_features  = DataLoader(force_path)
        virial_features  = DataLoader(virial_path)

        X_test_2  =  coord_features.prepare_data()
        X_test_3  =  force_features.prepare_data()
        X_test_4  =  virial_features.prepare_data()

        X_test_combined = np.concatenate((X_test_1, X_test_2, X_test_3, X_test_4), axis=1)
        X_test_combined_normalized = scaler.fit_transform(X_test_combined)
        X_test_combined_normalized = X_test_combined_normalized.reshape((X_test_combined_normalized.shape[0], X_test_combined_normalized.shape[1], 1))
        return X_test_combined_normalized, y_test


if __name__ == '__main__':
    train_box_path = r'CNN_Regression\data\training_data\set.000\box.npy'
    train_energy_path = r'CNN_Regression\data\training_data\set.000\energy.npy'
    train_coord_path = r'CNN_Regression\data\training_data\set.000\coord.npy'
    train_force_path = r'CNN_Regression\data\training_data\set.000\force.npy'
    train_virial_path = r'CNN_Regression\data\training_data\set.000\virial.npy'

    # X_train, X_val, y_train, y_val = get_train_dataset(train_energy_path, train_box_path)
    # X_train, X_val, y_train, y_val = get_train_dataset(train_energy_path, train_box_path, train_coord_path)
    X_train, X_val, y_train, y_val = get_train_dataset(train_energy_path, train_box_path, train_coord_path, train_force_path, train_virial_path)

    model = CNN_REGRESSION()
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mae'])
    # Define the EarlyStopping callback
    early_stopping = EarlyStopping(
        monitor='val_loss',    # Monitor the validation loss
        patience=10,           # Number of epochs with no improvement after which training will be stopped
        restore_best_weights=True,  # Restore model weights from the epoch with the best value of the monitored quantity
        verbose=1
    )
    # Train the model with early stopping
    history = model.fit(
        X_train, y_train, 
        epochs=500, 
        batch_size=16, 
        validation_data=(X_val, y_val),
        callbacks=[early_stopping]  # Pass the early stopping callback here
    )
    
    # Evaluate the model on the validation data
    val_loss, val_mae = model.evaluate(X_val, y_val)
    print(f'Validation MAE: {val_mae}')
    
    # Predict using the validation set
    predictions = model.predict(X_val)

    # Sample prediction
    print(f'Predicted energy: {predictions[0]}')
    print(f'Actual energy: {y_val[0]}')

    print('============================================================')
    test_box_path = r'CNN_Regression\data\validation_data\set.000\box.npy'
    test_energy_path = r'CNN_Regression\data\validation_data\set.000\energy.npy'
    test_coord_path = r'CNN_Regression\data\validation_data\set.000\coord.npy'
    test_force_path = r'CNN_Regression\data\validation_data\set.000\force.npy'
    test_virial_path = r'CNN_Regression\data\validation_data\set.000\virial.npy'
    # X_test, y_test = get_test_dataset(test_energy_path , test_box_path)
    # X_test, y_test = get_test_dataset(test_energy_path , test_box_path, test_coord_path)
    X_test, y_test = get_test_dataset(test_energy_path , test_box_path, test_coord_path, test_force_path, test_virial_path)

    # Evaluate the model on the test data
    test_loss, test_mae = model.evaluate(X_test, y_test)
    print(f'Test Loss: {test_loss}')
    print(f'Test MAE: {test_mae}')

    # Make predictions
    predictions = model.predict(X_test)

    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

    # Calculate metrics
    mse = mean_squared_error(y_test, predictions)
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print(f'MSE: {mse}')
    print(f'MAE: {mae}')
    print(f'R^2: {r2}')

    import matplotlib.pyplot as plt

    # Plot predicted vs actual energy values
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, predictions, color='blue', label='Predicted vs Actual')
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', linestyle='--', label='Ideal fit')
    plt.xlabel('Actual Energy')
    plt.ylabel('Predicted Energy')
    plt.title('Predicted vs Actual Energy')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot residuals
    residuals = y_test - predictions.flatten()
    plt.figure(figsize=(10, 6))
    plt.scatter(predictions, residuals, color='purple', label='Residuals')
    plt.axhline(0, color='red', linestyle='--')
    plt.xlabel('Predicted Energy')
    plt.ylabel('Residuals')
    plt.title('Residuals Plot')
    plt.legend()
    plt.grid(True)
    plt.show()

