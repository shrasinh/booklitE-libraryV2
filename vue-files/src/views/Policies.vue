<template>
<title>Library Policies</title>
<h1>Library Policies</h1>
<br>
<strong>For issuing:</strong>
<ul>
  <li>
    You can issued the book if the available number of copies of the book for issue is greater than zero.
  </li>
  <li>
    You can only hold one issued copy of the book at any given time.
  </li>
  <li>
    The books will be available in the <RouterLink to="/user/issuedbooks">Issued Books</RouterLink> section.
  </li>
  <li>Normal members will have to return the book within <em>7 days</em> of issuing, or the access to the book will be
    automatically revoked. They will be able to issue at most <em>5 books</em> at a time.</li>
  <li>
    Subscribed members will have to return the book within <em>14 days</em> of issuing, or the access to the book will
    be automatically revoked. They will be able to issue at most <em>10 books</em> at a time.
  </li>
  <li>Subscribed members will also get the access to text-to-speech version of the book within those period.</li>
</ul>
<strong>For purchasing:</strong>
<ul>
  <li>Before purchasing, you have to fill up the payment details section of the <RouterLink to="/accountdetails">account</RouterLink>
    page.</li>
  <li>You can purchase the book anytime you want, regardless of the <em>available number of copies for issue</em> status
    of the book.</li>
  <li>
    You purchase only one copy of the book.
  </li>
  <li>
    The purchased books will be available for download in the <RouterLink to="/user/purchasedbooks">Purchased Books</RouterLink>
    section.
  </li>
</ul>
<strong>For become a subscribed member:</strong>
<ul>
  <li>You have to fill up the payment details section of the <RouterLink to="/accountdetails">account</RouterLink> page.</li>
  <li>Then register via the membership section of the <RouterLink to="/accountdetails">account</RouterLink> page.</li>
  <li>The return date of the books issued before becoming a member will remain the same. So you will enjoy the benefits
    of extended return dates only on the books that you issue after becoming a member.</li>
</ul>
</template>