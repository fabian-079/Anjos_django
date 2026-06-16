-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 06, 2026 at 02:39 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `anjos_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `auth_group`
--

CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL,
  `name` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_group_permissions`
--

CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `auth_permission`
--

CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `auth_permission`
--

INSERT INTO `auth_permission` (`id`, `name`, `content_type_id`, `codename`) VALUES
(1, 'Can add log entry', 1, 'add_logentry'),
(2, 'Can change log entry', 1, 'change_logentry'),
(3, 'Can delete log entry', 1, 'delete_logentry'),
(4, 'Can view log entry', 1, 'view_logentry'),
(5, 'Can add permission', 2, 'add_permission'),
(6, 'Can change permission', 2, 'change_permission'),
(7, 'Can delete permission', 2, 'delete_permission'),
(8, 'Can view permission', 2, 'view_permission'),
(9, 'Can add group', 3, 'add_group'),
(10, 'Can change group', 3, 'change_group'),
(11, 'Can delete group', 3, 'delete_group'),
(12, 'Can view group', 3, 'view_group'),
(13, 'Can add content type', 4, 'add_contenttype'),
(14, 'Can change content type', 4, 'change_contenttype'),
(15, 'Can delete content type', 4, 'delete_contenttype'),
(16, 'Can view content type', 4, 'view_contenttype'),
(17, 'Can add session', 5, 'add_session'),
(18, 'Can change session', 5, 'change_session'),
(19, 'Can delete session', 5, 'delete_session'),
(20, 'Can view session', 5, 'view_session'),
(21, 'Can add user', 6, 'add_user'),
(22, 'Can change user', 6, 'change_user'),
(23, 'Can delete user', 6, 'delete_user'),
(24, 'Can view user', 6, 'view_user'),
(25, 'Can add category', 7, 'add_category'),
(26, 'Can change category', 7, 'change_category'),
(27, 'Can delete category', 7, 'delete_category'),
(28, 'Can view category', 7, 'view_category'),
(29, 'Can add customization', 8, 'add_customization'),
(30, 'Can change customization', 8, 'change_customization'),
(31, 'Can delete customization', 8, 'delete_customization'),
(32, 'Can view customization', 8, 'view_customization'),
(33, 'Can add order', 9, 'add_order'),
(34, 'Can change order', 9, 'change_order'),
(35, 'Can delete order', 9, 'delete_order'),
(36, 'Can view order', 9, 'view_order'),
(37, 'Can add role', 10, 'add_role'),
(38, 'Can change role', 10, 'change_role'),
(39, 'Can delete role', 10, 'delete_role'),
(40, 'Can view role', 10, 'view_role'),
(41, 'Can add repair', 11, 'add_repair'),
(42, 'Can change repair', 11, 'change_repair'),
(43, 'Can delete repair', 11, 'delete_repair'),
(44, 'Can view repair', 11, 'view_repair'),
(45, 'Can add product', 12, 'add_product'),
(46, 'Can change product', 12, 'change_product'),
(47, 'Can delete product', 12, 'delete_product'),
(48, 'Can view product', 12, 'view_product'),
(49, 'Can add order item', 13, 'add_orderitem'),
(50, 'Can change order item', 13, 'change_orderitem'),
(51, 'Can delete order item', 13, 'delete_orderitem'),
(52, 'Can view order item', 13, 'view_orderitem'),
(53, 'Can add notification', 14, 'add_notification'),
(54, 'Can change notification', 14, 'change_notification'),
(55, 'Can delete notification', 14, 'delete_notification'),
(56, 'Can view notification', 14, 'view_notification'),
(57, 'Can add model has role', 15, 'add_modelhasrole'),
(58, 'Can change model has role', 15, 'change_modelhasrole'),
(59, 'Can delete model has role', 15, 'delete_modelhasrole'),
(60, 'Can view model has role', 15, 'view_modelhasrole'),
(61, 'Can add favorite', 16, 'add_favorite'),
(62, 'Can change favorite', 16, 'change_favorite'),
(63, 'Can delete favorite', 16, 'delete_favorite'),
(64, 'Can view favorite', 16, 'view_favorite'),
(65, 'Can add cart item', 17, 'add_cartitem'),
(66, 'Can change cart item', 17, 'change_cartitem'),
(67, 'Can delete cart item', 17, 'delete_cartitem'),
(68, 'Can view cart item', 17, 'view_cartitem');

-- --------------------------------------------------------

--
-- Table structure for table `cart_items`
--

CREATE TABLE `cart_items` (
  `id` bigint(20) NOT NULL,
  `quantity` int(11) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `product_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cart_items`
--

INSERT INTO `cart_items` (`id`, `quantity`, `created_at`, `updated_at`, `product_id`, `user_id`) VALUES
(3, 1, '2026-04-05 06:07:46.330585', '2026-04-05 06:07:46.330585', 4, 4);

-- --------------------------------------------------------

--
-- Table structure for table `categories`
--

CREATE TABLE `categories` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext DEFAULT NULL,
  `image` varchar(500) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`id`, `name`, `description`, `image`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'Anillos', 'Anillos de diferentes materiales y diseños', NULL, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000'),
(2, 'Collares', 'Collares y cadenas elegantes', NULL, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000'),
(3, 'Pulseras', 'Pulseras y brazaletes', NULL, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000'),
(4, 'Aretes', 'Aretes y pendientes', NULL, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000'),
(5, 'Relojes', 'Relojes de lujo', NULL, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000'),
(6, 'Dijes', 'Dijes y colgantes', NULL, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000');

-- --------------------------------------------------------

--
-- Table structure for table `customizations`
--

CREATE TABLE `customizations` (
  `id` bigint(20) NOT NULL,
  `jewelry_type` varchar(100) NOT NULL,
  `design` varchar(255) NOT NULL,
  `stones` varchar(100) NOT NULL,
  `finish` varchar(100) NOT NULL,
  `color` varchar(100) NOT NULL,
  `material` varchar(100) NOT NULL,
  `size` varchar(50) DEFAULT NULL,
  `engraving` varchar(255) DEFAULT NULL,
  `special_instructions` longtext DEFAULT NULL,
  `estimated_price` decimal(10,2) DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `admin_notes` longtext DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `assigned_technician` varchar(100) DEFAULT NULL,
  `cost_accepted` tinyint(1) DEFAULT NULL,
  `client_counter_offer` decimal(10,2) DEFAULT NULL,
  `client_negotiation_note` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customizations`
--

INSERT INTO `customizations` (`id`, `jewelry_type`, `design`, `stones`, `finish`, `color`, `material`, `size`, `engraving`, `special_instructions`, `estimated_price`, `status`, `admin_notes`, `is_active`, `created_at`, `updated_at`, `user_id`, `assigned_technician`, `cost_accepted`, `client_counter_offer`, `client_negotiation_note`) VALUES
(1, 'Pulsera', 'clasico', 'Esmeralda', 'Brillante', 'Dorado', 'Plata', NULL, NULL, NULL, 90000.00, 'in_progress', '', 1, '2026-04-05 14:58:53.710712', '2026-04-05 18:47:19.227113', 2, 'Luisa Fernández', 1, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `django_admin_log`
--

CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) UNSIGNED NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `django_content_type`
--

CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_content_type`
--

INSERT INTO `django_content_type` (`id`, `app_label`, `model`) VALUES
(1, 'admin', 'logentry'),
(3, 'auth', 'group'),
(2, 'auth', 'permission'),
(4, 'contenttypes', 'contenttype'),
(17, 'infrastructure', 'cartitem'),
(7, 'infrastructure', 'category'),
(8, 'infrastructure', 'customization'),
(16, 'infrastructure', 'favorite'),
(15, 'infrastructure', 'modelhasrole'),
(14, 'infrastructure', 'notification'),
(9, 'infrastructure', 'order'),
(13, 'infrastructure', 'orderitem'),
(12, 'infrastructure', 'product'),
(11, 'infrastructure', 'repair'),
(10, 'infrastructure', 'role'),
(6, 'infrastructure', 'user'),
(5, 'sessions', 'session');

-- --------------------------------------------------------

--
-- Table structure for table `django_migrations`
--

CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_migrations`
--

INSERT INTO `django_migrations` (`id`, `app`, `name`, `applied`) VALUES
(1, 'contenttypes', '0001_initial', '2026-03-26 02:05:27.745393'),
(2, 'contenttypes', '0002_remove_content_type_name', '2026-03-26 02:05:27.792680'),
(3, 'auth', '0001_initial', '2026-03-26 02:05:27.973094'),
(4, 'auth', '0002_alter_permission_name_max_length', '2026-03-26 02:05:28.014730'),
(5, 'auth', '0003_alter_user_email_max_length', '2026-03-26 02:05:28.022500'),
(6, 'auth', '0004_alter_user_username_opts', '2026-03-26 02:05:28.030136'),
(7, 'auth', '0005_alter_user_last_login_null', '2026-03-26 02:05:28.035879'),
(8, 'auth', '0006_require_contenttypes_0002', '2026-03-26 02:05:28.038889'),
(9, 'auth', '0007_alter_validators_add_error_messages', '2026-03-26 02:05:28.043863'),
(10, 'auth', '0008_alter_user_username_max_length', '2026-03-26 02:05:28.048534'),
(11, 'auth', '0009_alter_user_last_name_max_length', '2026-03-26 02:05:28.055695'),
(12, 'auth', '0010_alter_group_name_max_length', '2026-03-26 02:05:28.065693'),
(13, 'auth', '0011_update_proxy_permissions', '2026-03-26 02:05:28.072478'),
(14, 'auth', '0012_alter_user_first_name_max_length', '2026-03-26 02:05:28.077202'),
(15, 'infrastructure', '0001_initial', '2026-03-26 02:05:29.165638'),
(16, 'admin', '0001_initial', '2026-03-26 02:05:29.283693'),
(17, 'admin', '0002_logentry_remove_auto_add', '2026-03-26 02:05:29.292612'),
(18, 'admin', '0003_logentry_add_action_flag_choices', '2026-03-26 02:05:29.299372'),
(19, 'sessions', '0001_initial', '2026-03-26 02:05:29.333160'),
(20, 'infrastructure', '0002_customization_assigned_technician_and_more', '2026-04-05 07:01:17.679226'),
(21, 'infrastructure', '0003_customization_cost_accepted_repair_cost_accepted', '2026-04-05 07:16:08.420963'),
(22, 'infrastructure', '0004_customization_client_counter_offer_and_more', '2026-04-05 15:30:57.208024');

-- --------------------------------------------------------

--
-- Table structure for table `django_session`
--

CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `django_session`
--

INSERT INTO `django_session` (`session_key`, `session_data`, `expire_date`) VALUES
('2yiefucw70f3yd1ybloalbudurvaqdne', '.eJxVjMsOwiAQRf-FtSG8YVy69xvIwIBUDU1KuzL-uzbpQrf3nHNfLOK2triNssSJ2JlJdvrdEuZH6TugO_bbzPPc12VKfFf4QQe_zlSel8P9O2g42rfOkjTmUrWrSEJmkZINVaMwoCGAcqDJKBtIgDSgvBfJg1XosgZTvGPvD-gWNx8:1w9PrN:Q3JFZd_FhYlQA6Lmo1skYJhAhvUTHHbxdfqIs98vUzk', '2026-04-19 15:58:01.970367'),
('5pm6spzefpwp6fmkc1htn2xccymrvm8j', '.eJxVjDsOwjAQBe_iGln-xawp6XOGaNdr4wCypTipEHeHSCmgfTPzXmLCbS3T1tMyzSwuworT70YYH6nugO9Yb03GVtdlJrkr8qBdjo3T83q4fwcFe_nW2edgwxDAahqYrAFkDUafs1aMBM6RJ-PAhqQwe8XRJ6WBGAYwBEq8P9SrN3g:1w9Ptg:UF-W8CyVP151qAai1rT2q9Qfow3TZigum5nTMBxPjPQ', '2026-04-19 16:00:24.798384'),
('8su1pyaq8l2l73fya7umqgm1up6di0hq', '.eJxVjDsOwjAQBe_iGln-xawp6XOGaNdr4wCypTipEHeHSCmgfTPzXmLCbS3T1tMyzSwuworT70YYH6nugO9Yb03GVtdlJrkr8qBdjo3T83q4fwcFe_nW2edgwxDAahqYrAFkDUafs1aMBM6RJ-PAhqQwe8XRJ6WBGAYwBEq8P9SrN3g:1w9PqZ:VkmYDB3v-xNDI3--v0abhR1DXma4PDrCsv7DtzMrYZw', '2026-04-19 15:57:11.865836'),
('ewrdkj5qbbpailjszfqi1ft3mqzdt74s', '.eJxVjMsOwiAQRf-FtSG8YVy69xvIwIBUDU1KuzL-uzbpQrf3nHNfLOK2triNssSJ2JlJdvrdEuZH6TugO_bbzPPc12VKfFf4QQe_zlSel8P9O2g42rfOkjTmUrWrSEJmkZINVaMwoCGAcqDJKBtIgDSgvBfJg1XosgZTvGPvD-gWNx8:1w9Ppc:2zlBgiiHPu0bqF1Ubv9tLBfingRxQNuy_xfLlQ4PN8A', '2026-04-19 15:56:12.274120'),
('j1ah35p08wk5v89o0bqmju70kb90s4sy', '.eJxVjMsOwiAQRf-FtSG8YVy69xvIwIBUDU1KuzL-uzbpQrf3nHNfLOK2triNssSJ2JlJdvrdEuZH6TugO_bbzPPc12VKfFf4QQe_zlSel8P9O2g42rfOkjTmUrWrSEJmkZINVaMwoCGAcqDJKBtIgDSgvBfJg1XosgZTvGPvD-gWNx8:1w9Pq5:Z1e6lD5qj_LhmdnrTCDVkAPPd3CYLlSfiYXJGkPRhSI', '2026-04-19 15:56:41.822239'),
('l5aaa6sos9hfq8nc3f0jxulhdojo3vqo', 'eyJndWVzdF9mYXZvcml0ZXMiOlsxXSwiZ3Vlc3RfY2FydCI6eyIxIjoxfX0:1w9T54:Tdnrl1efFfAsP7DQLCjuW8cKp5M_FBJFFh0-ONVIJY4', '2026-04-19 19:24:22.958041'),
('lz0xgta4sm23zakkf8v84g6rmxuk40c0', '.eJxVjMsOwiAQRf-FtSG8YVy69xvIwIBUDU1KuzL-uzbpQrf3nHNfLOK2triNssSJ2JlJdvrdEuZH6TugO_bbzPPc12VKfFf4QQe_zlSel8P9O2g42rfOkjTmUrWrSEJmkZINVaMwoCGAcqDJKBtIgDSgvBfJg1XosgZTvGPvD-gWNx8:1w9PqZ:PPWZ9H298BJrfjoZnolQ3SmYzFaB_uqdrH7SZRGGMOU', '2026-04-19 15:57:11.848781'),
('msuwh3gi26yj4585q6yohu5s8vpd65hs', '.eJxVjMsOwiAQRf-FtSG8YVy69xvIwIBUDU1KuzL-uzbpQrf3nHNfLOK2triNssSJ2JlJdvrdEuZH6TugO_bbzPPc12VKfFf4QQe_zlSel8P9O2g42rfOkjTmUrWrSEJmkZINVaMwoCGAcqDJKBtIgDSgvBfJg1XosgZTvGPvD-gWNx8:1w9Pwy:8kdQCg3nspQpmQD9yL2iKm6OaM-bdxRwdvHHdbgX2wk', '2026-04-19 16:03:48.327052'),
('t5i3ag6z2nvzps9q89t6x9x005wtkksk', '.eJxVjMsOwiAURP-FtSFcqiAu3fsN5D5AqgaS0q6M_26bdKGL2cw5M28VcZlLXHqa4ijqoqw6_HaE_Ex1A_LAem-aW52nkfSm6J12fWuSXtfd_Tso2Mu6Tm6As2cnRGwA0dOAhg2CC9avIX-0yZzAsWGbOWTrMwzsMCQQyaA-X-VaOBk:1w9PrO:zST2XDKiopkd-L0mLv-P4U5KVRwHypSCHbuBUI8uFa8', '2026-04-19 15:58:02.000190'),
('tj008linbazsyztpuh1u8stsg8s3jnts', '.eJxVjMsOwiAURP-FtSFcqiAu3fsN5D5AqgaS0q6M_26bdKGL2cw5M28VcZlLXHqa4ijqoqw6_HaE_Ex1A_LAem-aW52nkfSm6J12fWuSXtfd_Tso2Mu6Tm6As2cnRGwA0dOAhg2CC9avIX-0yZzAsWGbOWTrMwzsMCQQyaA-X-VaOBk:1w9PqZ:4ljlQxLR36pTrdxzm7yy1GF_8VGSyKe27tnqk4nTTMA', '2026-04-19 15:57:11.908317'),
('vj06j323hjdmpd0fvajhclvgegyhjajs', '.eJxVjMsOwiAQRf-FtSG8YVy69xvIwIBUDU1KuzL-uzbpQrf3nHNfLOK2triNssSJ2JlJdvrdEuZH6TugO_bbzPPc12VKfFf4QQe_zlSel8P9O2g42rfOkjTmUrWrSEJmkZINVaMwoCGAcqDJKBtIgDSgvBfJg1XosgZTvGPvD-gWNx8:1w9PyM:S84tLazUMplfRImK8F0Q5SWcPyl3_xz1ct-xk2q7aQY', '2026-04-19 16:05:14.346982'),
('wbgbkpx4lq3bf0zyiugtpx9bls50r0q3', '.eJxVjDsOwjAQBe_iGln-xawp6XOGaNdr4wCypTipEHeHSCmgfTPzXmLCbS3T1tMyzSwuworT70YYH6nugO9Yb03GVtdlJrkr8qBdjo3T83q4fwcFe_nW2edgwxDAahqYrAFkDUafs1aMBM6RJ-PAhqQwe8XRJ6WBGAYwBEq8P9SrN3g:1w9Pwy:4idKnnDiEIErRrZC6OLFtgKLJdpcqlDsDFhDQgg7hd0', '2026-04-19 16:03:48.350978'),
('wq2zp1kd3b3n568pmbkl3621fif1szvy', '.eJxVjDsOwjAQBe_iGln-xawp6XOGaNdr4wCypTipEHeHSCmgfTPzXmLCbS3T1tMyzSwuworT70YYH6nugO9Yb03GVtdlJrkr8qBdjo3T83q4fwcFe_nW2edgwxDAahqYrAFkDUafs1aMBM6RJ-PAhqQwe8XRJ6WBGAYwBEq8P9SrN3g:1w9PyM:KtV-voRZ35HzxStnBfCTrYzkLOfdvtnXok07zaGWP4A', '2026-04-19 16:05:14.383506');

-- --------------------------------------------------------

--
-- Table structure for table `favorites`
--

CREATE TABLE `favorites` (
  `id` bigint(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `customization_id` bigint(20) DEFAULT NULL,
  `product_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `favorites`
--

INSERT INTO `favorites` (`id`, `created_at`, `updated_at`, `customization_id`, `product_id`, `user_id`) VALUES
(6, '2026-04-05 05:43:22.629155', '2026-04-05 05:43:22.629155', NULL, 1, 4),
(7, '2026-04-05 05:43:23.917471', '2026-04-05 05:43:23.917471', NULL, 2, 4),
(9, '2026-04-05 06:52:47.288381', '2026-04-05 06:52:47.288381', NULL, 4, 2),
(10, '2026-04-05 06:52:49.710033', '2026-04-05 06:52:49.710033', NULL, 2, 2);

-- --------------------------------------------------------

--
-- Table structure for table `model_has_roles`
--

CREATE TABLE `model_has_roles` (
  `id` bigint(20) NOT NULL,
  `model_id` bigint(20) NOT NULL,
  `role_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `model_has_roles`
--

INSERT INTO `model_has_roles` (`id`, `model_id`, `role_id`) VALUES
(1, 1, 1),
(2, 3, 2),
(3, 4, 2),
(4, 5, 2),
(5, 6, 2),
(6, 7, 2);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` bigint(20) NOT NULL,
  `message` longtext NOT NULL,
  `is_read` tinyint(1) NOT NULL,
  `notification_type` varchar(30) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `customization_id` bigint(20) DEFAULT NULL,
  `order_id` bigint(20) DEFAULT NULL,
  `repair_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `message`, `is_read`, `notification_type`, `created_at`, `customization_id`, `order_id`, `repair_id`, `user_id`) VALUES
(1, 'Nueva orden creada por loren. Número de orden: ORD-1775365965717. Total: $39,270,000.00', 1, 'NEW_ORDER', '2026-04-05 05:12:45.750191', NULL, 1, NULL, 1),
(2, 'Nueva orden creada por fabian. Número de orden: ORD-1775372254105. Total: $32,963,000.00', 1, 'NEW_ORDER', '2026-04-05 06:57:34.142755', NULL, 2, NULL, 1),
(3, 'Nueva solicitud de reparación de fabian. N° REP-1775372311527', 1, 'NEW_REPAIR', '2026-04-05 06:58:31.543844', NULL, NULL, 1, 1),
(4, 'Nueva solicitud de reparación de fabian. N° REP-1775400961124', 1, 'NEW_REPAIR', '2026-04-05 14:56:01.157356', NULL, NULL, 2, 1),
(5, 'El costo estimado de tu reparación N° REP-1775400961124 fue actualizado a $500,000', 1, 'REPAIR_UPDATE', '2026-04-05 14:56:41.753483', NULL, NULL, 2, 2),
(6, 'Se asignó el técnico Andrés Gómez a tu reparación N° REP-1775400961124', 1, 'REPAIR_UPDATE', '2026-04-05 14:56:41.753483', NULL, NULL, 2, 2),
(7, 'El cliente fabian ha aceptado el costo estimado de $500,000 de la reparación N° REP-1775400961124', 1, 'REPAIR_UPDATE', '2026-04-05 14:57:10.556870', NULL, NULL, 2, 1),
(8, 'El costo estimado de tu reparación N° REP-1775400961124 fue actualizado a $200,000', 1, 'REPAIR_UPDATE', '2026-04-05 14:57:47.535470', NULL, NULL, 2, 2),
(9, 'Nueva personalización de fabian: Pulsera - clasico', 1, 'NEW_CUSTOMIZATION', '2026-04-05 14:58:53.720409', 1, NULL, NULL, 1),
(10, 'Se asignó el técnico Luisa Fernández a tu personalización #1', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 15:16:14.273296', 1, NULL, NULL, 2),
(11, 'El precio estimado de tu personalización fue actualizado a $100,000.00', 1, 'PRICE_UPDATE', '2026-04-05 15:16:14.273296', 1, NULL, NULL, 2),
(12, 'El cliente fabian ha rechazado el precio estimado de $100,000 de la personalización #1', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 15:17:17.381870', 1, NULL, NULL, 1),
(13, 'El cliente fabian propone $950,000 para la personalización #1', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 15:35:48.471550', 1, NULL, NULL, 1),
(14, 'El cliente fabian ha rechazado el costo estimado de $80,000 de la reparación N° REP-1775400961124', 1, 'REPAIR_UPDATE', '2026-04-05 15:57:12.517162', NULL, NULL, 2, 1),
(15, 'El cliente fabian propone $55,000 para la reparación N° REP-1775400961124: \"Mi presupuesto es menor\"', 1, 'REPAIR_UPDATE', '2026-04-05 15:57:12.550175', NULL, NULL, 2, 1),
(16, '¡Buenas noticias! Tu propuesta de $55,000 para la reparación N° REP-1775400961124 fue aceptada.', 0, 'REPAIR_UPDATE', '2026-04-05 15:57:12.568730', NULL, NULL, 2, 2),
(17, 'El cliente fabian ha aceptado el precio estimado de $300,000 de la personalización #1', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 15:58:02.600019', 1, NULL, NULL, 1),
(18, 'El cliente fabian ha rechazado el precio estimado de $300,000 de la personalización #1', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 15:58:02.643823', 1, NULL, NULL, 1),
(19, 'El cliente fabian propone $220,000 para la personalización #1: \"Propongo este valor\"', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 15:58:02.668216', 1, NULL, NULL, 1),
(20, 'Tu propuesta para la personalización #1 no fue aceptada. El precio estimado original de $300,000 sigue vigente.', 0, 'CUSTOMIZATION_UPDATE', '2026-04-05 15:58:02.689166', 1, NULL, NULL, 2),
(21, '¡Buenas noticias! Tu propuesta de $220,000 para la personalización #1 fue aceptada.', 0, 'CUSTOMIZATION_UPDATE', '2026-04-05 15:58:02.717932', 1, NULL, NULL, 2),
(24, 'El precio estimado de tu personalización fue actualizado a $50,000.00', 0, 'PRICE_UPDATE', '2026-04-05 18:39:45.828017', 1, NULL, NULL, 2),
(25, 'El precio estimado de tu personalización #1 fue establecido en $100,000', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 18:46:15.823650', 1, NULL, NULL, 2),
(26, 'El cliente fabian ha rechazado el precio estimado de $100,000 de la personalización #1', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 18:46:42.354160', 1, NULL, NULL, 1),
(27, 'El cliente fabian propone $90,000 para la personalización #1', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 18:46:51.657946', 1, NULL, NULL, 1),
(28, '¡Buenas noticias! Tu propuesta de $90,000 para la personalización #1 fue aceptada.', 1, 'CUSTOMIZATION_UPDATE', '2026-04-05 18:47:19.229860', 1, NULL, NULL, 2);

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` bigint(20) NOT NULL,
  `order_number` varchar(50) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `tax` decimal(10,2) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `status` varchar(20) NOT NULL,
  `shipping_address` varchar(500) NOT NULL,
  `billing_address` varchar(500) NOT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `payment_method` varchar(20) NOT NULL,
  `notes` longtext DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `order_number`, `subtotal`, `tax`, `total`, `status`, `shipping_address`, `billing_address`, `phone`, `payment_method`, `notes`, `is_active`, `created_at`, `updated_at`, `user_id`) VALUES
(1, 'ORD-1775365965717', 33000000.00, 6270000.00, 39270000.00, 'PROCESSING', 'fdssad', 'hgffghgh', '54564456', 'EFECTIVO', NULL, 1, '2026-04-05 05:12:45.726730', '2026-04-05 05:18:01.433077', 4),
(2, 'ORD-1775372254105', 27700000.00, 5263000.00, 32963000.00, 'PENDING', 'calle 10', 'calle 10', '3123131', 'PSE', NULL, 1, '2026-04-05 06:57:34.118739', '2026-04-05 06:57:34.118739', 2);

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `id` bigint(20) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `order_id` bigint(20) NOT NULL,
  `product_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_items`
--

INSERT INTO `order_items` (`id`, `quantity`, `price`, `created_at`, `updated_at`, `order_id`, `product_id`) VALUES
(1, 2, 16500000.00, '2026-04-05 05:12:45.729430', '2026-04-05 05:12:45.729430', 1, 1),
(2, 1, 8200000.00, '2026-04-05 06:57:34.120739', '2026-04-05 06:57:34.120739', 2, 2),
(3, 1, 19500000.00, '2026-04-05 06:57:34.127080', '2026-04-05 06:57:34.127080', 2, 4);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL,
  `material` varchar(100) DEFAULT NULL,
  `color` varchar(100) DEFAULT NULL,
  `finish` varchar(100) DEFAULT NULL,
  `stones` varchar(100) DEFAULT NULL,
  `size` varchar(50) DEFAULT NULL,
  `image` varchar(500) DEFAULT NULL,
  `gallery` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`gallery`)),
  `is_featured` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `category_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `name`, `description`, `price`, `stock`, `material`, `color`, `finish`, `stones`, `size`, `image`, `gallery`, `is_featured`, `is_active`, `created_at`, `updated_at`, `category_id`) VALUES
(1, 'Anillo de Compromiso Diamante 1 Quilate', 'Exquisito anillo de oro blanco 18K con brillante diamante central de 1 quilate certificado GIA.', 16500000.00, 4, 'Oro blanco 18K', 'Blanco', 'Pulido brillante', 'Diamante 1ct GIA', NULL, '/uploads/products/051b5deb-316c-43a0-bf51-75f3248d50dc.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-05 05:12:45.720654', 1),
(2, 'Anillo Ópalo Australiano Vintage', 'Anillo vintage de época con ópalo australiano genuino de alta calidad.', 8200000.00, 4, 'Oro amarillo 18K', 'Verde iridiscente', 'Matizado antiguo', 'Ópalo australiano + diamantes', NULL, '/uploads/products/749f9f8a-b4cb-4f03-8d1e-1231c7527114.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-05 06:57:34.108226', 1),
(3, 'Anillo Esmeralda Colombiana Premium', 'Anillo de lujo con esmeralda verde intenso de las minas de Muzo, Colombia.', 14200000.00, 3, 'Oro blanco 14K', 'Verde profundo Muzo', 'Pulido espejo', 'Esmeralda colombiana + diamantes', NULL, '/uploads/products/d4844582-9143-4331-88fa-aa362ca8ce58.jpg', NULL, 0, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 1),
(4, 'Anillo Rubí Birmano Signature', 'Anillo de firma con rubí rojo fuego de Birmania de 2 quilates.', 19500000.00, 2, 'Oro rojo 18K', 'Rojo intenso fuego', 'Pulido brillante', 'Rubí Birmano 2ct', NULL, '/uploads/products/e50d2629-244f-4a6c-9963-501f4bf963b9.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-05 06:57:34.115223', 1),
(5, 'Collar Cadena de Oro Blanco 45cm', 'Cadena delicada y versátil de oro blanco 18K.', 5600000.00, 12, 'Oro blanco 18K', 'Blanco plateado', 'Pulido brillante', 'Ninguno', NULL, '/uploads/products/103a508d-7c51-412e-85de-405810e11e77.jpg', NULL, 0, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 2),
(6, 'Collar de Perlas Cultivadas Agua Dulce', 'Elegante collar con 16 perlas blancas cultivadas de agua dulce de 8mm.', 10500000.00, 6, 'Plata 925', 'Blanco crema natural', 'Satinado perla', 'Perlas agua dulce cultivadas', NULL, '/uploads/products/a4930eef-4b1e-4fb7-acc0-0de26a059355.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 2),
(7, 'Collar Choker Diamantes 0.5ct', 'Collar ajustado de gala con 30 diamantes naturales.', 13200000.00, 4, 'Plata 950', 'Blanco brillante', 'Pulido espejo', 'Diamantes naturales 0.5ct', NULL, '/uploads/products/e5a3626c-b985-476c-a3c7-f1e2e2b59686.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 2),
(8, 'Pulsera Tenis Diamantes 2ct', 'Pulsera de tenis de lujo con 50 diamantes naturales.', 22500000.00, 5, 'Oro blanco 18K', 'Blanco diamantado', 'Pulido brillante', 'Diamantes naturales 2ct', NULL, '/uploads/products/a9fa87c0-b8be-4e53-be6e-ec509d440f10.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 3),
(10, 'Pulsera Tres Zafiros Azules Oro', 'Pulsera sofisticada con tres zafiros azules naturales de Sri Lanka.', 12000000.00, 3, 'Oro amarillo 14K', 'Azul profundo natural', 'Pulido matizado', 'Zafiros naturales Sri Lanka x3', NULL, '/uploads/products/3421aa7d-fb3c-4909-ae76-e91a95ee8ed5.jpg', NULL, 0, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 3),
(11, 'Aretes Gota Cuarzo Rosa 18K', 'Hermosos aretes colgantes en forma de gota con cuarzo rosa genuino.', 5200000.00, 8, 'Oro rosado 18K', 'Rosa natural pálido', 'Pulido brillante', 'Cuarzo rosa natural', NULL, '/uploads/products/e066663e-3677-458a-b766-23afb453e114.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 4),
(12, 'Aretes Brillante Diamante Certificado', 'Clásicos aretes de botón con diamantes naturales de 0.5 quilates cada uno.', 9800000.00, 6, 'Oro blanco 18K', 'Blanco brillante', 'Pulido brillante', 'Diamantes naturales GIA 0.5ct c/u', NULL, '/uploads/products/7253bfa1-52da-4b92-be3d-bb9292ab7973.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 4),
(13, 'Reloj Suizo Automático Oro Amarillo', 'Reloj de pulsera suizo con movimiento automático ETA 2824.', 32000000.00, 2, 'Oro amarillo 18K', 'Oro cálido', 'Cepillado y pulido', 'Índices diamantes', NULL, '/uploads/products/ba61e10a-abde-4a00-bdf4-052e523e63ef.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 5),
(14, 'Reloj Cuarzo Suizo Plata Elegante', 'Reloj de cuarzo precisión suiza con bisel de plata 925.', 14600000.00, 4, 'Plata 925', 'Plateado espejo', 'Pulido espejo', 'Diamantes naturales x12', NULL, '/uploads/products/b503bd70-fbd6-4131-80bf-b9edf5e34772.jpg', NULL, 0, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 5),
(15, 'Dije Corazón de Oro Blanco 18K', 'Delicado y romántico dije en forma de corazón de oro blanco 18K.', 2200000.00, 15, 'Oro blanco 18K', 'Blanco plateado', 'Pulido brillante', 'Ninguno', NULL, '/uploads/products/fb717466-b185-4e8b-b74b-2ec5825c08fe.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 6),
(17, 'Dije Cruz Filigrana Oro Rosado', 'Dije cruz de tamaño mediano en oro rosado 14K.', 2800000.00, 12, 'Oro rosado 14K', 'Oro rosado cálido', 'Pulido matizado filigrana', 'Ninguno', NULL, '/uploads/products/83a378d0-9fb3-424e-82b6-ab2481c764d7.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-05 04:55:49.781871', 6),
(19, 'Dije Ángel Guardián Oro Blanco', 'Hermoso dije con figura de ángel protector en oro blanco 18K.', 3200000.00, 10, 'Oro blanco 18K', 'Blanco plateado', 'Pulido brillante', 'Ninguno', NULL, '/uploads/products/c3d48a87-0117-4e83-b9ef-8dc7968bcb00.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 6),
(20, 'Dije Inicial Personalizado Oro 18K', 'Dije letra inicial personalizado en oro amarillo 18K.', 2550000.00, 16, 'Oro amarillo 18K', 'Oro cálido natural', 'Pulido brillante', 'Ninguno', NULL, '/uploads/products/e91340a0-7c14-4d19-a0a3-c9ccbfa253d2.jpg', NULL, 0, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 6),
(21, 'Anillo de Compromiso Esmeralda', 'Hermoso anillo de compromiso con esmeralda natural y diamantes', 2500.00, 5, 'Oro 18k', 'Verde', 'Brillante', 'Esmeralda, Diamantes', '', '/uploads/products/f5fb2c69-c190-424c-85c8-e874f8327d1e.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 1),
(24, 'Anillo Diamante Solitario', 'Anillo de compromiso con diamante natural de 1 quilate.', 5750000.00, 5, 'Oro Blanco 18k', 'Blanco', 'Brillante', 'Diamante 1ct', NULL, '/uploads/products/0d7e01fe-4c62-4343-a645-7e602f88ec00.jpg', NULL, 1, 1, '2026-04-04 22:35:51.000000', '2026-04-04 22:35:51.000000', 1);

-- --------------------------------------------------------

--
-- Table structure for table `repairs`
--

CREATE TABLE `repairs` (
  `id` bigint(20) NOT NULL,
  `repair_number` varchar(50) NOT NULL,
  `customer_name` varchar(255) NOT NULL,
  `description` longtext NOT NULL,
  `phone` varchar(50) NOT NULL,
  `image` varchar(500) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `estimated_cost` decimal(10,2) DEFAULT NULL,
  `technician_notes` longtext DEFAULT NULL,
  `notes` longtext DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `assigned_technician_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  `assigned_technician_text` varchar(100) DEFAULT NULL,
  `cost_accepted` tinyint(1) DEFAULT NULL,
  `client_counter_offer` decimal(10,2) DEFAULT NULL,
  `client_negotiation_note` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `repairs`
--

INSERT INTO `repairs` (`id`, `repair_number`, `customer_name`, `description`, `phone`, `image`, `status`, `estimated_cost`, `technician_notes`, `notes`, `is_active`, `created_at`, `updated_at`, `assigned_technician_id`, `user_id`, `assigned_technician_text`, `cost_accepted`, `client_counter_offer`, `client_negotiation_note`) VALUES
(1, 'REP-1775372311527', 'fabian', 'fdsssss', '3107245628', '/uploads/repairs/Logo.png', 'PENDING', NULL, NULL, 'dfssssss', 1, '2026-04-05 06:58:31.527249', '2026-04-05 07:07:25.989913', NULL, 2, 'Luisa Fernández', NULL, NULL, NULL),
(2, 'REP-1775400961124', 'fabian', 'dfsdssdf', '54564456', '/uploads/repairs/Logo.png', 'PENDING', NULL, NULL, NULL, 1, '2026-04-05 14:56:01.124920', '2026-04-05 15:57:12.568730', NULL, 2, 'Andrés Gómez', NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `id` bigint(20) NOT NULL,
  `name` varchar(50) NOT NULL,
  `guard_name` varchar(50) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`id`, `name`, `guard_name`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 'admin', 'web', 1, '2026-03-26 02:05:29.393803', '2026-03-26 02:05:29.395029'),
(2, 'cliente', 'web', 1, '2026-03-26 02:05:29.396909', '2026-03-26 02:05:29.396909');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` bigint(20) NOT NULL,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `address` longtext DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `email_verified_at` datetime(6) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `password`, `last_login`, `is_superuser`, `name`, `email`, `phone`, `address`, `is_active`, `is_staff`, `email_verified_at`, `created_at`, `updated_at`) VALUES
(1, 'pbkdf2_sha256$600000$kRuzaXfUraSIPDKd8pRKpo$gAdSeRvSsuYpsnHGwIIGzH1RhjoynHtgHU9rXECQl10=', '2026-04-05 18:49:38.921587', 1, 'Administrador', 'admin@anjos.com', NULL, NULL, 1, 1, NULL, '2026-03-26 02:05:29.642168', '2026-03-26 02:05:29.642168'),
(2, 'pbkdf2_sha256$600000$mS5P9cLCeB7M0weiqY7fUU$6kPIy1/UNIf5TQVELOFAXazmsPe2ThCt0ydWRCQHtSs=', '2026-04-05 18:47:28.720549', 1, 'fabian', 'fabian@gmail.com', NULL, NULL, 1, 1, NULL, '2026-03-26 02:06:21.632589', '2026-03-26 02:06:21.632589'),
(3, 'pbkdf2_sha256$600000$aoA01tuW6cYj5EHOokN1vJ$Xsex8t4Li5TaQPF40lJE/+RR6cHdR/kVlGdBkj672RE=', '2026-04-05 16:05:14.372860', 0, 'Fabian Vargas', 'fabianvq7@gmail.com', '3133232513', 'carrera 160', 1, 0, NULL, '2026-03-26 02:07:59.880856', '2026-03-26 02:07:59.880856'),
(4, 'pbkdf2_sha256$600000$mvXPHjYorrWFfU91v0GVeR$3gLNSic2iG2R+/7vTp6Q8o2gInuyGkIxEdt7Slao79w=', '2026-04-05 06:03:04.355058', 0, 'loren', 'loren@gmail.com', NULL, NULL, 1, 0, NULL, '2026-04-05 05:10:15.614955', '2026-04-05 05:10:15.614955'),
(5, 'pbkdf2_sha256$600000$F3zTOAIUDOuZBZWuWCZp4q$F+g8KeTPQ6D5RDzQ0wGHLX5SqwlarGwpjLYVOktTktM=', '2026-04-05 06:29:11.401349', 0, 'sadds', 'queubeutauloubra-2445@yopmail.com', '54564456', NULL, 1, 0, NULL, '2026-04-05 06:29:09.561311', '2026-04-05 06:29:09.561311'),
(6, 'pbkdf2_sha256$600000$6rqlELmC2iA5X6SwkB5cpB$S9Hc/ivTaJSlAQMewNraKHEEqy0OiCHkVc/aggQmLwY=', '2026-04-05 06:29:59.940322', 0, 'sads', 'alt.jl-cdve6ft@yopmail.com', NULL, NULL, 1, 0, NULL, '2026-04-05 06:29:58.378956', '2026-04-05 06:29:58.378956'),
(7, 'pbkdf2_sha256$600000$ygwyIkixjWHgt2bcf24Qa9$1unUl4OOVI/rme0cW7VPn3IbpQwz67Harit/+YgySDs=', '2026-04-05 06:42:09.715868', 0, 'Loren Sanchez', '280903loren@gmail.com', NULL, NULL, 1, 0, NULL, '2026-04-05 06:42:06.633601', '2026-04-05 06:42:06.633601');

-- --------------------------------------------------------

--
-- Table structure for table `users_groups`
--

CREATE TABLE `users_groups` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `group_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users_user_permissions`
--

CREATE TABLE `users_user_permissions` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `permission_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `auth_group`
--
ALTER TABLE `auth_group`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  ADD KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`);

--
-- Indexes for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`);

--
-- Indexes for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `cart_items_user_id_product_id_e4319647_uniq` (`user_id`,`product_id`),
  ADD KEY `cart_items_product_id_9398bb89_fk_products_id` (`product_id`);

--
-- Indexes for table `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `customizations`
--
ALTER TABLE `customizations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customizations_user_id_ab3eda6d_fk_users_id` (`user_id`);

--
-- Indexes for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  ADD KEY `django_admin_log_user_id_c564eba6_fk_users_id` (`user_id`);

--
-- Indexes for table `django_content_type`
--
ALTER TABLE `django_content_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`);

--
-- Indexes for table `django_migrations`
--
ALTER TABLE `django_migrations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `django_session`
--
ALTER TABLE `django_session`
  ADD PRIMARY KEY (`session_key`),
  ADD KEY `django_session_expire_date_a5c62663` (`expire_date`);

--
-- Indexes for table `favorites`
--
ALTER TABLE `favorites`
  ADD PRIMARY KEY (`id`),
  ADD KEY `favorites_customization_id_06224837_fk_customizations_id` (`customization_id`),
  ADD KEY `favorites_product_id_20deaadd_fk_products_id` (`product_id`),
  ADD KEY `favorites_user_id_d60eb79f_fk_users_id` (`user_id`);

--
-- Indexes for table `model_has_roles`
--
ALTER TABLE `model_has_roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `model_has_roles_model_id_role_id_928eac76_uniq` (`model_id`,`role_id`),
  ADD KEY `model_has_roles_role_id_1fe3f278_fk_roles_id` (`role_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `notifications_customization_id_382c2440_fk_customizations_id` (`customization_id`),
  ADD KEY `notifications_order_id_2e72753f_fk_orders_id` (`order_id`),
  ADD KEY `notifications_repair_id_3f62035a_fk_repairs_id` (`repair_id`),
  ADD KEY `notifications_user_id_468e288d_fk_users_id` (`user_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `orders_user_id_7e2523fb_fk_users_id` (`user_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_items_order_id_412ad78b_fk_orders_id` (`order_id`),
  ADD KEY `order_items_product_id_dd557d5a_fk_products_id` (`product_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`),
  ADD KEY `products_category_id_a7a3a156_fk_categories_id` (`category_id`);

--
-- Indexes for table `repairs`
--
ALTER TABLE `repairs`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `repair_number` (`repair_number`),
  ADD KEY `repairs_assigned_technician_id_b48d25d4_fk_users_id` (`assigned_technician_id`),
  ADD KEY `repairs_user_id_2a7bc481_fk_users_id` (`user_id`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `users_groups`
--
ALTER TABLE `users_groups`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_groups_user_id_group_id_fc7788e8_uniq` (`user_id`,`group_id`),
  ADD KEY `users_groups_group_id_2f3517aa_fk_auth_group_id` (`group_id`);

--
-- Indexes for table `users_user_permissions`
--
ALTER TABLE `users_user_permissions`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `users_user_permissions_user_id_permission_id_3b86cbdf_uniq` (`user_id`,`permission_id`),
  ADD KEY `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` (`permission_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `auth_group`
--
ALTER TABLE `auth_group`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `auth_permission`
--
ALTER TABLE `auth_permission`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=69;

--
-- AUTO_INCREMENT for table `cart_items`
--
ALTER TABLE `cart_items`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `customizations`
--
ALTER TABLE `customizations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `django_content_type`
--
ALTER TABLE `django_content_type`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `django_migrations`
--
ALTER TABLE `django_migrations`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `favorites`
--
ALTER TABLE `favorites`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `model_has_roles`
--
ALTER TABLE `model_has_roles`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT for table `repairs`
--
ALTER TABLE `repairs`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `users_groups`
--
ALTER TABLE `users_groups`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users_user_permissions`
--
ALTER TABLE `users_user_permissions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `auth_group_permissions`
--
ALTER TABLE `auth_group_permissions`
  ADD CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`);

--
-- Constraints for table `auth_permission`
--
ALTER TABLE `auth_permission`
  ADD CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`);

--
-- Constraints for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD CONSTRAINT `cart_items_product_id_9398bb89_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `cart_items_user_id_74745f54_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `customizations`
--
ALTER TABLE `customizations`
  ADD CONSTRAINT `customizations_user_id_ab3eda6d_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `django_admin_log`
--
ALTER TABLE `django_admin_log`
  ADD CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  ADD CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `favorites`
--
ALTER TABLE `favorites`
  ADD CONSTRAINT `favorites_customization_id_06224837_fk_customizations_id` FOREIGN KEY (`customization_id`) REFERENCES `customizations` (`id`),
  ADD CONSTRAINT `favorites_product_id_20deaadd_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  ADD CONSTRAINT `favorites_user_id_d60eb79f_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `model_has_roles`
--
ALTER TABLE `model_has_roles`
  ADD CONSTRAINT `model_has_roles_model_id_05331b44_fk_users_id` FOREIGN KEY (`model_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `model_has_roles_role_id_1fe3f278_fk_roles_id` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`);

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_customization_id_382c2440_fk_customizations_id` FOREIGN KEY (`customization_id`) REFERENCES `customizations` (`id`),
  ADD CONSTRAINT `notifications_order_id_2e72753f_fk_orders_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  ADD CONSTRAINT `notifications_repair_id_3f62035a_fk_repairs_id` FOREIGN KEY (`repair_id`) REFERENCES `repairs` (`id`),
  ADD CONSTRAINT `notifications_user_id_468e288d_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_user_id_7e2523fb_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_order_id_412ad78b_fk_orders_id` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
  ADD CONSTRAINT `order_items_product_id_dd557d5a_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`);

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_category_id_a7a3a156_fk_categories_id` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`);

--
-- Constraints for table `repairs`
--
ALTER TABLE `repairs`
  ADD CONSTRAINT `repairs_assigned_technician_id_b48d25d4_fk_users_id` FOREIGN KEY (`assigned_technician_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `repairs_user_id_2a7bc481_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `users_groups`
--
ALTER TABLE `users_groups`
  ADD CONSTRAINT `users_groups_group_id_2f3517aa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  ADD CONSTRAINT `users_groups_user_id_f500bee5_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `users_user_permissions`
--
ALTER TABLE `users_user_permissions`
  ADD CONSTRAINT `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  ADD CONSTRAINT `users_user_permissions_user_id_92473840_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
