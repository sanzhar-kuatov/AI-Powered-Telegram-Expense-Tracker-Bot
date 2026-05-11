-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 11, 2026 at 10:09 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */
;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */
;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */
;
/*!40101 SET NAMES utf8mb4 */
;
--
-- Database: `expense_bot`
--

-- --------------------------------------------------------
--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `name`)
VALUES (3, 'Clothes'),
  (8, 'Education'),
  (6, 'Entertainment'),
  (1, 'Food'),
  (5, 'Health'),
  (4, 'Home'),
  (7, 'Other'),
  (2, 'Transport'),
  (9, 'Utilities');
-- --------------------------------------------------------
--
-- Table structure for table `conversations`
--

CREATE TABLE `conversations` (
  `id` int(11) NOT NULL,
  `telegram_id` bigint(20) NOT NULL,
  `user_message` text NOT NULL,
  `bot_reply` text NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
--
-- Dumping data for table `conversations`
--

INSERT INTO `conversations` (
    `id`,
    `telegram_id`,
    `user_message`,
    `bot_reply`,
    `created_at`
  )
VALUES (
    1,
    7818513811,
    'Gyoza 5',
    '✅ *Expense Saved!*\n\n📝 Item: gyoza\n💰 Amount: RM 5.00\n🏷️ Category: *Food*\n📊 Confidence: 🟢 High (96%)',
    '2026-05-07 21:18:27'
  ),
  (
    2,
    7818513811,
    'On 05.05.206 I got chicken rice for 15rm',
    '✅ *Expense Saved!*\n\n📝 Item: chicken rice\n💰 Amount: RM 15.00\n🏷️ Category: *Food*\n📊 Confidence: 🟢 High (98%)',
    '2026-05-07 21:19:42'
  ),
  (
    3,
    7818513811,
    'Tape - 2rm',
    '✅ *Expense Saved!*\n\n📝 Item: Tape\n💰 Amount: RM 2.00\n🏷️ Category: *Home*\n📊 Confidence: 🟢 High (85%)',
    '2026-05-07 21:21:18'
  ),
  (
    4,
    7818513811,
    'Mobile network - 25',
    '✅ *Expense Saved!*\n\n📅 Date: 2026-05-07\n📝 Item: Mobile network\n💰 Amount: RM 25.00\n🏷️ Category: *Transport*\n📊 Confidence: 🔴 Low (25%)',
    '2026-05-07 21:54:32'
  ),
  (
    5,
    7818513811,
    'Yesterday i paid for wifi 149rm',
    '✅ *Expense Saved!*\n\n📅 Date: 2026-05-06\n📝 Item: wifi\n💰 Amount: RM 149.00\n🏷️ Category: *Home*\n📊 Confidence: 🟢 High (92%)',
    '2026-05-07 21:54:58'
  ),
  (
    6,
    7818513811,
    'give me report for 04.05.2026-07.05.2026',
    'Report generated for 2026-05-04 to 2026-05-07.',
    '2026-05-07 21:55:59'
  ),
  (
    7,
    7818513811,
    'Electricity and water - 100rm',
    '✅ *Expense Saved!*\n\n📅 Date: 2026-05-07\n📝 Item: Electricity and water\n💰 Amount: RM 100.00\n🏷️ Category: *Utilities*\n📊 Confidence: 🟢 High (95%)',
    '2026-05-07 22:04:12'
  ),
  (
    8,
    7818513811,
    'protein smoothie 7.25',
    '✅ *Expense Saved!*\n\n🆔 ID: `7`\n📅 Date: 2026-05-07\n📝 Item: protein smoothie\n💰 Amount: RM 7.25\n🏷️ Category: *Food*\n📊 Confidence: 🟢 High (95%)\n\n_To edit this expense, mention its ID or say \'wrong ...\'_',
    '2026-05-07 22:48:18'
  ),
  (
    9,
    7818513811,
    'wrong 7, Chocolate Protein Smoothie',
    '✏️ *Expense Updated!*\n\n🆔 ID: `7`\n📝 Item: protein smoothie\n💰 Amount: RM 0.00\n🏷️ Category: Food\n📅 Date: 2026-05-07\n\n✅ Changed *amount* → `0`',
    '2026-05-07 22:48:52'
  ),
  (
    10,
    7818513811,
    'ID 7, name - Chocolate Protein Smoothie, price - 7.25rm',
    '⚠️ Could not update expense `ID 7`.\nPlease check the ID and try again.',
    '2026-05-07 22:49:29'
  ),
  (
    11,
    7818513811,
    'ID 7 - price 7.25rm',
    '✏️ *Expense Updated!*\n\n🆔 ID: `7`\n📝 Item: protein smoothie\n💰 Amount: RM 7.25\n🏷️ Category: Food\n📅 Date: 2026-05-07\n\n✅ Changed *amount* → `7.25`',
    '2026-05-07 22:49:42'
  ),
  (
    12,
    7818513811,
    'give report for 01.01.2025-01.06.2026',
    'Report generated: 2025-01-01 to 2026-06-01.',
    '2026-05-07 23:02:10'
  ),
  (
    13,
    7818513811,
    'Mixed rice 9.50',
    '✅ *Expense Saved!*\n\n🆔 ID: `10`\n📅 Date: 2026-05-08\n📝 Item: mixed rice\n💰 Amount: RM 9.50\n🏷️ Category: *Food*\n📊 Confidence: 🟢 High (95%)\n\n_To edit this expense, mention its ID or say \'wrong ...\'_',
    '2026-05-08 12:54:13'
  ),
  (
    14,
    7818513811,
    'Report for 19.04.2026-08.05.2026',
    'Report generated: 2026-04-19 to 2026-05-08.',
    '2026-05-08 12:55:57'
  ),
  (
    15,
    7818513811,
    'Yesterday I bought chicken rice for 15 rm',
    '✅ *Expense Saved!*\n\n🆔 ID: `11`\n📅 Date: 2026-05-10\n📝 Item: chicken rice\n💰 Amount: RM 15.00\n🏷️ Category: *Food*\n📊 Confidence: 🟢 High (95%)\n\n_To edit this expense, mention its ID or say \'wrong ...\'_',
    '2026-05-11 15:24:31'
  );
-- --------------------------------------------------------
--
-- Table structure for table `expenses`
--

CREATE TABLE `expenses` (
  `id` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `description` varchar(255) NOT NULL,
  `amount` decimal(10, 2) NOT NULL,
  `category_id` int(11) NOT NULL,
  `expense_date` date NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
--
-- Dumping data for table `expenses`
--

INSERT INTO `expenses` (
    `id`,
    `user_id`,
    `description`,
    `amount`,
    `category_id`,
    `expense_date`,
    `created_at`
  )
VALUES (
    1,
    7818513811,
    'gyoza',
    5.00,
    1,
    '2026-05-07',
    '2026-05-07 21:18:26'
  ),
  (
    2,
    7818513811,
    'chicken rice',
    15.00,
    1,
    '2026-05-07',
    '2026-05-07 21:19:42'
  ),
  (
    3,
    7818513811,
    'Tape',
    2.00,
    4,
    '2026-05-07',
    '2026-05-07 21:21:18'
  ),
  (
    4,
    7818513811,
    'Mobile network',
    25.00,
    2,
    '2026-05-07',
    '2026-05-07 21:54:32'
  ),
  (
    5,
    7818513811,
    'wifi',
    149.00,
    4,
    '2026-05-06',
    '2026-05-07 21:54:58'
  ),
  (
    6,
    7818513811,
    'Electricity and water',
    100.00,
    9,
    '2026-05-07',
    '2026-05-07 22:04:12'
  ),
  (
    7,
    7818513811,
    'protein smoothie',
    7.25,
    1,
    '2026-05-05',
    '2026-05-07 22:48:18'
  ),
  (
    8,
    7818513811,
    'reload tngo',
    10.00,
    2,
    '2026-05-04',
    '2026-05-07 22:53:08'
  ),
  (
    9,
    7818513811,
    'reload tngo',
    15.00,
    2,
    '2026-05-04',
    '2026-05-07 22:55:08'
  ),
  (
    10,
    7818513811,
    'mixed rice',
    9.50,
    1,
    '2026-05-08',
    '2026-05-08 12:54:12'
  ),
  (
    11,
    7818513811,
    'chicken rice',
    15.00,
    1,
    '2026-05-10',
    '2026-05-11 15:24:31'
  );
-- --------------------------------------------------------
--
-- Table structure for table `income`
--

CREATE TABLE `income` (
  `id` int(11) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `description` varchar(255) NOT NULL,
  `amount` decimal(10, 2) NOT NULL,
  `income_date` date NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
-- --------------------------------------------------------
--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `telegram_id` bigint(20) NOT NULL,
  `username` varchar(100) DEFAULT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;
--
-- Indexes for dumped tables
--

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);
--
-- Indexes for table `conversations`
--
ALTER TABLE `conversations`
ADD PRIMARY KEY (`id`),
  ADD KEY `telegram_id` (`telegram_id`);
--
-- Indexes for table `expenses`
--
ALTER TABLE `expenses`
ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `category_id` (`category_id`);
--
-- Indexes for table `income`
--
ALTER TABLE `income`
ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);
--
-- Indexes for table `users`
--
ALTER TABLE `users`
ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `telegram_id` (`telegram_id`);
--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
  AUTO_INCREMENT = 10;
--
-- AUTO_INCREMENT for table `conversations`
--
ALTER TABLE `conversations`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
  AUTO_INCREMENT = 16;
--
-- AUTO_INCREMENT for table `expenses`
--
ALTER TABLE `expenses`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
  AUTO_INCREMENT = 12;
--
-- AUTO_INCREMENT for table `income`
--
ALTER TABLE `income`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
MODIFY `id` int(11) NOT NULL AUTO_INCREMENT,
  AUTO_INCREMENT = 7;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `conversations`
--
ALTER TABLE `conversations`
ADD CONSTRAINT `conversations_ibfk_1` FOREIGN KEY (`telegram_id`) REFERENCES `users` (`telegram_id`);
--
-- Constraints for table `expenses`
--
ALTER TABLE `expenses`
ADD CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`telegram_id`),
  ADD CONSTRAINT `expenses_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`);
--
-- Constraints for table `income`
--
ALTER TABLE `income`
ADD CONSTRAINT `income_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`telegram_id`);
COMMIT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */
;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */
;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */
;