-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: db:3306
-- Generation Time: Apr 28, 2025 at 04:11 PM
-- Server version: 8.0.34
-- PHP Version: 8.2.8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `kamotost_HotelProject`
--

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `room_type` varchar(50) NOT NULL,
  `check_in_date` date NOT NULL,
  `check_out_date` date NOT NULL,
  `status` enum('pending','confirmed','canceled') DEFAULT 'pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `room_id` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

CREATE TABLE `requests` (
  `id` int NOT NULL,
  `user_id` int NOT NULL,
  `booking_id` int NOT NULL,
  `message` text NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `rooms`
--

CREATE TABLE `rooms` (
  `id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `room_type` varchar(50) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `description` text,
  `availability_status` enum('available','booked','maintenance') DEFAULT 'available',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` enum('guest','admin') DEFAULT 'guest',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `fk_booking_room` (`room_id`);

--
-- Indexes for table `requests`
--
ALTER TABLE `requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `booking_id` (`booking_id`);

--
-- Indexes for table `rooms`
--
ALTER TABLE `rooms`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `requests`
--
ALTER TABLE `requests`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `rooms`
--
ALTER TABLE `rooms`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `fk_booking_room` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`);

--
-- Constraints for table `requests`
--
ALTER TABLE `requests`
  ADD CONSTRAINT `requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `requests_ibfk_2` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

Insert into bookings

INSERT INTO `bookings` (`id`, `user_id`, `room_type`, `check_in_date`, `check_out_date`, `status`, `created_at`, `room_id`) VALUES
(6, 5, 'Standard', '2025-04-16', '2025-04-24', 'confirmed', '2025-04-14 16:20:51', 7),
(7, 5, 'Standard', '2025-04-16', '2025-04-24', 'confirmed', '2025-04-14 16:20:59', 2),
(8, 6, 'Standard', '2025-04-17', '2025-04-24', 'confirmed', '2025-04-14 17:10:24', 1),
(9, 6, 'Standard', '2025-04-17', '2025-04-24', 'confirmed', '2025-04-14 17:14:33', 10),
(13, 5, 'Deluxe', '2025-04-19', '2025-04-26', 'confirmed', '2025-04-16 15:19:15', 8),
(14, 6, 'Standard', '2025-04-25', '2025-04-26', 'confirmed', '2025-04-16 15:21:23', 7),
(15, 6, 'Standard', '2025-04-25', '2025-04-26', 'confirmed', '2025-04-16 15:45:33', 1);

Insert into users

INSERT INTO `users` (`id`, `name`, `password`, `role`, `created_at`) VALUES
(1, 'Daniella', 'dc47c8bc65f389181c4aa7f477b44539', 'guest', '2025-04-09 01:21:08'),
(5, 'Shingai', 'dc47c8bc65f389181c4aa7f477b44539', 'admin', '2025-04-09 20:08:40'),
(6, 'Tyler', 'a1dfa5c4294a5e51ee305d09adaeca83', 'guest', '2025-04-14 17:09:03'),
(7, 'Cole', '1d2691f43cfceb1ed3be05cf89822597', 'guest', '2025-04-15 19:00:27');

Insert into rooms

INSERT INTO `rooms` (`id`, `name`, `room_type`, `price`, `description`, `availability_status`, `created_at`) VALUES
(1, 'Room 101', 'Standard', 88.00, 'Cozy room with queen bed', 'available', '2025-04-14 13:48:11'),
(2, 'Room 102', 'Standard', 80.00, 'Great for solo travelers', 'available', '2025-04-14 13:48:11'),
(3, 'Room 201', 'Deluxe', 120.00, 'Spacious room with king bed and balcony', 'booked', '2025-04-14 13:48:11'),
(4, 'Room 202', 'Deluxe', 120.00, 'Deluxe with sea view', 'available', '2025-04-14 13:48:11'),
(6, 'Room 302', 'Executive Suite', 250.00, 'Executive with jacuzzi and workspace', 'maintenance', '2025-04-14 13:48:11'),
(7, 'Room 401', 'Standard', 85.00, 'Quiet room near garden', 'available', '2025-04-14 13:48:11'),
(8, 'Room 402', 'Deluxe', 130.00, 'Recently renovated with modern decor', 'available', '2025-04-14 13:48:11'),
(9, 'Room 501', 'Executive Suite', 220.00, 'Top floor with panoramic views', 'booked', '2025-04-14 13:48:11'),
(10, 'Room 502', 'Standard', 90.00, 'Budget-friendly with all essentials', 'available', '2025-04-14 13:48:11'),
(11, 'Room 101', 'Standard', 500.00, 'sample', NULL, '2025-04-23 20:27:15');

Insert into requests
