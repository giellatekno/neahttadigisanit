import { test, expect } from '@playwright/test';

test("saan has correct paradigm for vueʹlǧǧed", async ({ page }) => {
    // THIS TEST ASSUMES saan !!
    await page.goto("http://localhost:5000/detail/sms/fin/vueʹlǧǧed.html?no_compounds=true&lemma_match=true");

    // Check that we have 2 rows (why 2? see below)
    await expect(page.locator("css=div.entry_row")).toHaveCount(2);

    // the last row should be empty!
    const last_row = page.locator("css=div.entry_row:nth-child(2)");
    await expect(last_row).toBeEmpty();

    // Now check the first row

    // Check that the word and translation is correct
    const p = page.locator("css=div.entry_row:nth-child(1) > div.lexeme > p.lead");
    await expect(p).toContainText("vueʹlǧǧed");
    const meanings = page.locator("css=div.entry_row:nth-child(1) > div.lexeme > ul.meanings");
    await expect(meanings).toContainText("lähteä");

    /* The paradigm, as we expect it to be:
            prs. (täʹbbe) 	      prt. (jåhtta)
    Sg1 	(mon) vuâlǥam 	      vuõʹlǧǧem
    Sg2 	(ton) vuâlǥak 	      vuõʹlǧǧiǩ
    Sg3 	(son) vuâlgg 	      vuõʹlji
    Pl1 	(mij) vueʹlǧǧep       vuõʹljim
    Pl2 	(tij) vueʹlǧǧveʹted   vuõʹljid
    Pl3 	(sij) vueʹlǧǧe 	      vuõʹlǧǧe
    Sg4 	vueʹlget              vuõʹlǧǧeš

    prs. kielt.
        (täʹbbe jiõm) vueʹlg
    prt. kielt.
        (jåhtta jiõm) vuâlggam
    */
    // The table we're interested in checking is the one that's visible
    // (there are two tables, one is usually not visible)
    // So find the first table who's tbody is visible....

    // This locator was found by using
    // `pnpm exec playwright codegen`
    const miniparadigm = page.locator(".span8 > div").first();
    await expect(miniparadigm).toContainText("vuâlǥam", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuõʹlǧǧem", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuâlǥak", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuõʹlǧǧiǩ", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuâlgg", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuõʹlji", { useInnerText: true });
    await expect(miniparadigm).toContainText("vueʹlǧǧep", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuõʹljim", { useInnerText: true });
    await expect(miniparadigm).toContainText("vueʹlǧǧveʹted", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuõʹljid", { useInnerText: true });
    await expect(miniparadigm).toContainText("vueʹlǧǧe", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuõʹlǧǧe", { useInnerText: true });
    await expect(miniparadigm).toContainText("vueʹlget", { useInnerText: true });
    await expect(miniparadigm).toContainText("vuõʹlǧǧeš", { useInnerText: true });
});
