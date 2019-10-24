class MainController:
    def __init__(self, main_menu):
        self.main_menu = main_menu

    def write_chains(self, chains):
        # TODO check function
        wrong_chains = []
        for chain in chains:
            if self.valid_chain(chain):
                self.write_chain(chain)
            else:
                wrong_chains.append(chain)
        return wrong_chains

    def valid_chain(self, chain):
        if self.chain_count(chain) > 1:
            return False
        for job in chain.jobs:
            if self.job_count(job) > 1:
                return False
        return True

    def write_chain(self, chain):
        # TODO check function
        self.fill_chain(chain)
        for job in chain.jobs:
            self.fill_job(job)

    def fill_chain(self, chain):
        search_chain_form = self.main_menu.chain_search()
        if search_chain_form.chain_count(cadena=chain.chain, borrador=True) is 1:
            new_chain_form = search_chain_form.edit_chain(cadena=chain.chain, borrador=True)
        elif search_chain_form.chain_count(cadena=chain.chain, borrador=False) is 1:
            new_chain_form = search_chain_form.edit_chain(cadena=chain.chain, borrador=False)
        else:
            new_chain_form = self.main_menu.chain_new()

        new_chain_form.fill_form(chain)
        new_chain_form.send_form()

    def fill_job(self, job):
        search_job_form = self.main_menu.job_search()
        if search_job_form.job_count(jobname=job.jobname, borrador=True) is 1:
            new_job_form = search_job_form.edit_job(jobname=job.jobname, borrador=True)
        elif search_job_form.job_count(jobname=job.jobname, borrador=False) is 1:
            new_job_form = search_job_form.edit_job(cadena=job.jobname, borrador=False)
        else:
            new_job_form = self.main_menu.job_new()

        new_job_form.fill_form(job)
        new_job_form.send_form()

    def chain_count(self, chain):
        search_chain_form = self.main_menu.chain_search()
        count = search_chain_form.chain_count(cadena=chain.chain, borrador=True)
        return search_chain_form.chain_count(cadena=chain.chain, borrador=False) if count is 0 else count

    def job_count(self, job):
        search_job_form = self.main_menu.job_search()
        count = search_job_form.job_count(jobname=job.jobname, borrador=True)
        return search_job_form.job_count(jobname=job.jobname, borrador=False) if count is 0 else count
