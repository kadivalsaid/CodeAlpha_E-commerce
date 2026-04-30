function money(n){
  const x = Number(n || 0);
  return x.toFixed(2);
}

function getCookie(name){
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

async function postForm(url, formData){
  const csrfToken = getCookie('csrftoken');
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      ...(csrfToken ? {'X-CSRFToken': csrfToken} : {})
    },
    body: formData,
    credentials: 'same-origin'
  });
  return await res.json();
}

document.addEventListener('change', async (e) => {
  const input = e.target;
  if (!input.matches('[data-cart-qty]')) return;

  const itemId = input.getAttribute('data-item-id');
  const updateUrl = input.getAttribute('data-update-url');
  const qty = input.value;

  const fd = new FormData();
  fd.append('quantity', qty);

  try{
    const data = await postForm(updateUrl, fd);
    if (data && data.ok){
      const totalEl = document.querySelector('[data-cart-total]');
      if (totalEl) totalEl.textContent = money(data.cart_total);
    }
  }catch(err){
    // fallback: do nothing (user can refresh)
  }
});

