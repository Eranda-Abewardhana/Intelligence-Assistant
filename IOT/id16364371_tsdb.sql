-- phpMyAdmin SQL Dump
-- version 4.9.5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 22, 2021 at 04:58 AM
-- Server version: 10.3.16-MariaDB
-- PHP Version: 7.3.23

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `id16364371_tsdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `boards`
--

CREATE TABLE `boards` (
  `id` int(6) UNSIGNED NOT NULL,
  `last_request` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `User` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `gpio` int(2) NOT NULL,
  `State` int(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `boards`
--

INSERT INTO `boards` (`id`, `last_request`, `User`, `gpio`, `State`) VALUES
(182, '2021-03-20 00:28:06', 'Tharindu Sathsara', 4, 0),
(183, '2021-03-23 13:08:36', 'Tharindu Sathsara', 4, 1),
(184, '2021-03-25 04:33:51', 'Tharindu Sathsara', 2, 0),
(185, '2021-03-25 04:33:51', 'Tharindu Sathsara', 2, 1),
(186, '2021-03-25 04:33:52', 'Tharindu Sathsara', 2, 0),
(187, '2021-03-25 04:33:53', 'Tharindu Sathsara', 4, 0),
(188, '2021-03-25 04:33:54', 'Tharindu Sathsara', 2, 1),
(189, '2021-03-25 04:33:55', 'Tharindu Sathsara', 4, 1),
(190, '2021-06-26 15:44:33', 'admin', 2, 0),
(191, '2021-06-26 15:44:34', 'admin', 4, 0);

-- --------------------------------------------------------

--
-- Table structure for table `details`
--

CREATE TABLE `details` (
  `Data` text NOT NULL,
  `Value` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `details`
--

INSERT INTO `details` (`Data`, `Value`) VALUES
('SwitchDelay', '12');

-- --------------------------------------------------------

--
-- Table structure for table `outputs`
--

CREATE TABLE `outputs` (
  `id` int(6) UNSIGNED NOT NULL,
  `name` varchar(64) COLLATE utf8_unicode_ci DEFAULT NULL,
  `gpio` int(6) DEFAULT NULL,
  `state` int(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `outputs`
--

INSERT INTO `outputs` (`id`, `name`, `gpio`, `state`) VALUES
(1, 'Built-in LED', 2, 0),
(16, 'New Switch', 4, 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `boards`
--
ALTER TABLE `boards`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `outputs`
--
ALTER TABLE `outputs`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `boards`
--
ALTER TABLE `boards`
  MODIFY `id` int(6) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=192;

--
-- AUTO_INCREMENT for table `outputs`
--
ALTER TABLE `outputs`
  MODIFY `id` int(6) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
