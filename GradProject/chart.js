// Dashboard graph







// // Assuming the provided timestamp is in milliseconds
// var timestamp = 1714117281691;

// // Create a new Date object using the timestamp
// var date = new Date(timestamp);
// // Format the date into a readable string
// var formattedDate = date.toLocaleString();

// console.log(formattedDate); // Output: "4/11/2024, 11:21:21 PM" (this format may vary depending on your locale)
// -------------------------------------------------------------------
function bytesToMB(bytes) {
  return (bytes / (1024 * 1024)).toFixed(2); // Rounded to 2 decimal places
}

// Example usage:
const bytes = 745869312;
const megabytes = Number(bytesToMB(bytes));
console.log(megabytes + " MB");
