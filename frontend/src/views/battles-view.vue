
<template>

    <section class="current_battles">
        <div class="current_battles__card">
            <h2 class="section_name"> Текущие дуэли </h2>
        </div>

    </section>
    
    <section class="menu">

    </section>

</template>

<style scoped>

.current_battles {
    height: 90vh;
    min-height: 90vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.current_battles__card {
    width: 90%;
    height: 90%;
    padding: 24px;
    border-radius: 16px;
    background-color: white;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.section_name {
    text-align: center;
    width: 80%;
    font-size: 30px;
    font-weight: bold;
    padding: 0 0 7px 0;
    /* margin: 0 auto; */
    position: relative;
}

.section_name::after {
      content: "";
      position: absolute;
      left: 50%;
      bottom: 0;
      transform: translateX(-50%);
      width: 100%;
      height: 8px;
      clip-path: polygon(0 100%, 18% 60%, 50% 0, 82% 60%, 100% 100%);
      background: linear-gradient(
          90deg,
          transparent 0%,
          black 20%,
          black 80%,
          transparent 100%
      );
}


</style>

