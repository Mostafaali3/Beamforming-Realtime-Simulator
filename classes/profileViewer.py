import pyqtgraph as pg
from PyQt5.QtWidgets import QVBoxLayout, QFrame
import numpy as np
from classes.phasedArray import PhasedArray
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import logging
class ProfileViewer(QFrame):
    def __init__(self):
        super().__init__()
        self.current_phased_array = PhasedArray()
        # self.setBackground("#1E293B")
        self.current_mode = "Transmitting Mode"
        self.num_of_antennas = 1
        self.frequency = 2
        self.distance_between_recievers = 1
        self.transmitter_position = (50,50)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        
        self.wavelength = 1 / self.frequency
        self.theta = np.linspace(-np.pi, np.pi, 1000) 
        self.phase_shift = 2 * np.pi * self.distance_between_recievers / self.wavelength
        self.k = 2 * np.pi / self.wavelength

    
        self.ax = self.figure.add_subplot(111, polar=True)  
        # self.ax.set_title("Polar Beam Profile", va='bottom')
        # self.ax.set_rticks([0.25, 0.5, 0.75,1]) 
        self.ax.set_rticks([]) 
        self.ax.set_ylim(0, 1)
        # self.ax.set_thetamin(-90)   # Limit angular range to 0°–180° # to be in the safe zone 
        # self.ax.set_thetamax(90)

        self.animation = FuncAnimation(self.figure, self.update_plot, frames=np.arange(0, 2*np.pi, 0.01), 
                                        init_func=self.init_plot, blit=True, interval=50)

    def init_plot(self):
        self.line, = self.ax.plot([], [], color="b", linewidth=2, label="Beam Profile")
        self.ax.set_theta_zero_location("N")  # Set 0 degrees at the top
        self.figure.patch.set_facecolor("#1E293B")
        self.ax.patch.set_facecolor("#1E293B")
        self.ax.grid(color = "gray")
        self.ax.tick_params(axis='both', colors='white')  # Set tick label color
        # self.ax.set_rticks([0.5, 1, 1.5], color='purple') 
        # self.ax.set_theta_direction(-1)
        self.logger.info("Initialized the beam profile viewer")
        return self.line,
    
    def calculate_phase_shift(self, antenna, angle):
        dx = antenna.x_posision - self.transmitter_position[0]
        dy = antenna.y_posision - self.transmitter_position[1]
        distance = np.sqrt(dx**2 + dy**2)

        additional_distance = distance * np.cos(angle)

        return self.k * additional_distance

    def update_plot(self, frame):
        if (self.current_mode == "Recieving Mode"):
            beam_profile = self.calculate_recivers_beam_profile()
            
            # self.frequency = 2
            # self.wavelength = 1 / self.frequency
            # self.phase_shift = 2 * np.pi * self.distance_between_recievers / self.wavelength
            # self.k = 2 * np.pi / self.wavelength
            # amplitude = np.zeros_like(self.theta, dtype=np.complex128)
            # for antenna in self.current_phased_array.transmitters_list:
            #     phase_shift = self.calculate_phase_shift(antenna, self.theta)
            #     amplitude += np.exp(1j * (2 * np.pi * self.frequency * frame - phase_shift))

            # intensity = np.abs(amplitude) ** 2  
            # normalized_intensity = intensity / np.max(intensity) 
            self.line.set_data(np.linspace(0, 2 * np.pi, 1000), beam_profile)
            # self.ax.set_rmax(2)
            # self.ax.set_rticks([0.5, 1, 1.5, 2])
            return self.line,
        else:
            # self.frequency = self.current_phased_array.current_frequency
            # self.wavelength = 1/self.frequency
            # self.phase_shift = 2 * np.pi* self.current_phased_array.phase_shift
            # self.k = 2* np.pi/self.wavelength
            # amplitude = np.zeros_like(self.theta, dtype=np.complex128)
            # for antenna in self.current_phased_array.transmitters_list:
            #     phase_shift = self.calculate_phase_shift(antenna, self.theta)
            #     amplitude += np.exp(1j * (2 * np.pi * self.frequency * frame - phase_shift))
            # intensity = np.abs(amplitude) ** 2  
            # normalized_intensity = intensity / np.max(intensity) 
            if self.current_phased_array.geometry == "Linear":
                beam_profile = self.calculate_transmitters_beam_profile()
                # angles = np.linspace(0, 2 * np.pi, 1000)
                self.line.set_data(self.theta, beam_profile)
                # self.ax.set_rmax(2)
            else:
                beam_profile = self.calculate_curvilinear_transmitters_beam_profle()
                self.line.set_data(self.theta+np.pi/2, beam_profile)
                # self.ax.set_rmax(2)

            return self.line,
            
            
    def calculate_recivers_beam_profile(self):
        response = []
        angles = np.linspace(0, 2 * np.pi, 1000)  # Angles from 0 to 360 degrees
        if len(self.current_phased_array.transmitters_list) > 1:
            self.distance_between_recievers = abs(self.current_phased_array.transmitters_list[0].x_posision - self.current_phased_array.transmitters_list[1].x_posision)
        else:
            self.distance_between_recievers = 0
        # self.distance_between_recievers = abs(self.current_phased_array.transmitters_list[-1].x_posision - self.current_phased_array.transmitters_list[len(self.current_phased_array.transmitters_list) - 1].x_posision) 
        for theta in angles:
            # print(self.current_phased_array.reciver_phase_shift)
            phase_shifts = (2 * np.pi / (1/self.current_phased_array.current_frequency)) * np.arange(len(self.current_phased_array.transmitters_list)) * self.distance_between_recievers *( np.sin(theta) - np.sin(self.current_phased_array.reciver_phase_shift))
            array_response = np.sum(np.exp(1j * phase_shifts))  # Complex sum
            response.append(abs(array_response))
        response = np.array(response)
        return response / np.max(response)
    
    def calculate_curvilinear_transmitters_beam_profle(self):
        response = []
        angles = np.linspace(0, 2*np.pi, 1000)
        k = 2 * np.pi / (1/self.current_phased_array.current_frequency)
        for theta in angles:
            phase_shifts = []
            for i, transmitter in enumerate(self.current_phased_array.transmitters_list):
                delta_r = transmitter.x_posision * np.cos(theta) + transmitter.y_posision * np.sin(theta)
                phase_shift = k * delta_r - self.current_phased_array.phase_shift*i
                phase_shifts.append(phase_shift)
            array_response = np.sum(np.exp(1j*np.array(phase_shifts)))
            response.append(abs(array_response))
        response = np.array(response)
        return response / np.max(response)
        
        # phase_shifts = np.zeros(len(self.current_phased_array.transmitters_list))
        # array_factor = np.zeros_like(angles)
        # for i, transmitter in enumerate(self.current_phased_array.transmitters_list):
        #     delta_r = transmitter.x_posision * np.cos(angles) + transmitter.y_posision * np.sin(angles)
        #     array_factor += np.exp(1j * (2 * np.pi / (1/self.frequency) * delta_r + self.current_phased_array.phase_shift*i))
        # return np.abs(array_factor) / np.max(array_factor)
        
    def calculate_transmitters_beam_profile(self):
        response = []
        angles = np.linspace(0,2*np.pi,1000)
        k = 2 * np.pi /( 1/self.current_phased_array.current_frequency)
        
        if len(self.current_phased_array.transmitters_list) > 1:
            self.distance_between_recievers = abs(self.current_phased_array.transmitters_list[0].x_posision - self.current_phased_array.transmitters_list[1].x_posision)
        else:
            self.distance_between_recievers = 0
            
        for theta in angles:
            phase_shifts = k * np.arange(len(self.current_phased_array.transmitters_list)) * \
                       self.distance_between_recievers * np.sin(theta) - \
                       np.arange(len(self.current_phased_array.transmitters_list)) * self.current_phased_array.phase_shift
            # print(self.current_phased_array.phase_shift)
            array_response = np.sum(np.exp(1j * phase_shifts))
            response.append(abs(array_response))
        response = np.array(response)
        return response / np.max(response)
        
        # elif(self.current_mode == "Transmitting Mode"):
        #     self.frequency = 2
        #     self.wavelength = 1 / self.frequency
        #     self.phase_shift = 2 * np.pi * self.distance_between_recievers / self.wavelength
        #     self.k = 2 * np.pi / self.wavelength
        #     amplitude = np.zeros_like(self.theta, dtype=np.complex128)
        #     for antenna in self.current_phased_array.transmitters_list:
        #         phase_shift = self.calculate_phase_shift(antenna, self.theta)
        #         amplitude += np.exp(1j * (2 * np.pi * self.frequency * frame - phase_shift))

        #     intensity = np.abs(amplitude) ** 2  
        #     normalized_intensity = intensity / np.max(intensity) 
        #     self.line.set_data(self.theta, normalized_intensity)
        #     return self.line,


    # def update_plot(self):
    #     self.clear()
    #     angles_list = np.linspace(-90, 90, 500)
    #     angles_radian = np.radians(angles_list)
    #     wave_lengh = 3e8 / self.current_phased_array.current_frequency
    #     k = 2 * np.pi/wave_lengh
    #     number_of_transmitters = len(self.current_phased_array.transmitters_list)
    #     distance = self.current_phased_array.distance
    #     transmitters_positions = np.array([[transmitter.x_posision, transmitter.y_posision] for transmitter in self.current_phased_array.transmitters_list]) 
    #     beam_profile = []
    #     for theta in angles_radian:
    #         phase_shifts = k*(transmitters_positions[:,0] * np.cos(theta) + transmitters_positions[:, 1]*np.sin(theta))
    #         combined_field = np.sum(np.exp(1j * phase_shifts))
    #         beam_profile.append(np.abs(combined_field)**2)
    #     beam_profile = np.array(beam_profile)/np.max(beam_profile)
    #     self.plot(angles_list, beam_profile)
            
            ##idea for the new year , apply the modulation effect
                
